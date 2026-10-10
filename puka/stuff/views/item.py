import logging
from types import MappingProxyType

from django.db.models import Case, F, IntegerField, Prefetch, Sum, Value, When
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView, View
from django_htmx.http import HttpResponseLocation, trigger_client_event
from django_htmx.middleware import HtmxDetails

from puka.core.pagination import PageSizeMixin
from puka.core.views import get_template
from puka.stuff.forms import InventoryForm, ItemForm, ItemImportForm
from puka.stuff.importer import (
    ERRORS_SESSION_KEY,
    IMPORT_SESSION_KEY,
    ImportFormatError,
    failed_rows_csv,
    import_upload,
    template_csv,
)
from puka.stuff.models import Inventory, Item
from puka.stuff.services import adjust_inventory_quantity, create_item_from_form

logger = logging.getLogger(__name__)


class ItemListView(PageSizeMixin, ListView):
    context_object_name = "items"

    def get_template_names(self):
        partial = (
            "#results-partial"
            if (HtmxDetails(self.request).target or "").endswith("#item-results")
            else "#list-partial"
        )
        return get_template(self.request, "stuff/item_list.html", partial)

    def get_queryset(self):
        if "query" in self.request.GET:
            query = self.request.GET["query"]
            query_set = Item.objects.search(query)
            self.extra_context = {"query": query}
        else:
            query_set = Item.objects.all().order_by("name")

        # Restock order: below-minimum items first, then items whose minimum is
        # met, then items without a minimum. Keep the queryset's own ordering
        # (name, relevance, location code) within each group.
        ordering = query_set.query.order_by or ("name",)
        return (
            query_set.annotate(quantity=Sum("inventories__quantity", default=0))
            .annotate(
                reorder_rank=Case(
                    When(reorder_level__gt=0, quantity__lt=F("reorder_level"), then=Value(0)),
                    When(reorder_level__gt=0, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                ),
            )
            .order_by("reorder_rank", *ordering)
            .prefetch_related(
                Prefetch("inventories", queryset=Inventory.objects.select_related("location")),
                "tags",
            )
        )


class ItemDetailView(DetailView):
    model = Item
    context_object_name = "item"
    extra_context = MappingProxyType({"bookmark_delete_url": "stuff:bookmark-delete"})

    def get_template_names(self):
        partial = (
            "#reorder-partial"
            if (HtmxDetails(self.request).target or "").endswith("#item-reorder-status")
            else "#detail-partial"
        )
        return get_template(self.request, "stuff/item_detail.html", partial)

    def get_queryset(self):
        return Item.objects.annotate(
            total_quantity=Sum("inventories__quantity", default=0),
        ).prefetch_related(
            Prefetch("inventories", queryset=Inventory.objects.select_related("location")),
            "tags",
            "bookmarks__tags",
        )


class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy("stuff:item-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")

    def form_valid(self, form):
        self.object: Item = create_item_from_form(form)
        return HttpResponseRedirect(self.get_success_url())


class ItemImportView(FormView):
    form_class = ItemImportForm
    template_name = "stuff/item_import.html"

    def get_template_names(self):
        return get_template(self.request, "stuff/item_import.html", "#import-partial")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["import_summary"] = self.request.session.get(IMPORT_SESSION_KEY)
        return context

    def form_valid(self, form):
        upload = form.cleaned_data["csv_file"]
        try:
            result = import_upload(upload)
        except ImportFormatError as error:
            form.add_error("csv_file", str(error))
            return self.form_invalid(form)

        self.request.session[IMPORT_SESSION_KEY] = {
            "filename": upload.name,
            "total": result.total,
            "imported": result.imported,
            "failed": len(result.failed),
        }
        if result.failed:
            self.request.session[ERRORS_SESSION_KEY] = failed_rows_csv(result.failed)
        else:
            self.request.session.pop(ERRORS_SESSION_KEY, None)
        return HttpResponseRedirect(self.request.path)


def item_import_template(_request):
    response = HttpResponse(template_csv(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="item-import-template.csv"'
    return response


def item_import_errors(request):
    csv_text = request.session.get(ERRORS_SESSION_KEY)
    if not csv_text:
        raise Http404
    response = HttpResponse(csv_text, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="item-import-errors.csv"'
    return response


class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy("stuff:item-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


class ItemDeleteView(View):
    def post(self, _request, pk):
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        return HttpResponseLocation(reverse("stuff:item-list"), target="#content")


def adjust_inventory(request, pk):
    quantity = int(request.POST.get("quantity", 0))
    inventory = get_object_or_404(Inventory, pk=pk)
    adjust_inventory_quantity(inventory, quantity)
    response = HttpResponse(str(inventory.quantity), content_type="text/plain")
    return trigger_client_event(response, "inventoryChanged", {"item_id": inventory.item_id})


class InventoryCreateView(CreateView):
    model = Inventory
    form_class = InventoryForm

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")

    def get_initial(self):
        return {"item": self.kwargs["pk"]}


class InventoryUpdateView(UpdateView):
    model = Inventory
    form_class = InventoryForm

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


class InventoryDeleteView(View):
    def post(self, _request, pk):
        inventory = get_object_or_404(Inventory, pk=pk)
        item_id = inventory.item.id
        inventory.delete()
        return HttpResponseLocation(
            reverse("stuff:item-detail", kwargs={"pk": item_id}),
            target="#content",
        )
