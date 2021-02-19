import { useRef } from "react";
import { useSearchParams } from "react-router-dom";

function SearchPage() {
  let queryRef = useRef<HTMLInputElement>(null);
  let [searchParams, setSearchParams] = useSearchParams({ q: "", t: "" });
  let query = searchParams.get("q");
  let tag = searchParams.getAll("t");

  // Use the form's "submit" event to persist
  // the query to the browser's address bar
  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (null !== queryRef.current) {
      setSearchParams({ q: queryRef.current.value, t: ["foo", "bar"] });
    }
  }

  return (
    <div>
      <p>The current query is "{query}".</p>
      <p>The current tag is "{tag.join(", ")}".</p>

      <form onSubmit={handleSubmit}>
        <input name="q" defaultValue={query ?? ""} ref={queryRef} />
      </form>
    </div>
  );
}

export default SearchPage;
