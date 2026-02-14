# Script for populating the database. You can run it as:
#
#     mix run priv/repo/seeds.exs
#
# Inside the script, you can read and write to any of your
# repositories directly:
#
#     Puka.Repo.insert!(%Puka.SomeSchema{})
#
# We recommend using the bang functions (`insert!`, `update!`
# and so on) as they will fail if something goes wrong.

alias Puka.Bookmarks
alias Puka.Tags

# Create 10 tags first
tags = [
  "elixir",
  "programming",
  "webdev",
  "devops",
  "design",
  "learning",
  "tools",
  "productivity",
  "fun",
  "resources"
]

Enum.each(tags, fn name ->
  Tags.create_tag(%{name: name})
end)

# Create 100 bookmarks with appropriate tags
bookmarks = [
  %{
    title: "Elixir School",
    url: "https://elixirschool.com",
    description: "Lessons about the Elixir programming language",
    tags: "elixir,learning,programming"
  },
  %{
    title: "Hex Docs",
    url: "https://hexdocs.pm",
    description: "Documentation for Hex packages",
    tags: "elixir,resources,programming"
  },
  %{
    title: "Elixir Forum",
    url: "https://elixirforum.com",
    description: "Community forum for Elixir developers",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Phoenix Framework",
    url: "https://phoenixframework.org",
    description: "Productive. Reliable. Fast. A web framework for Elixir",
    tags: "elixir,webdev,programming"
  },
  %{
    title: "LiveView Hero",
    url: "https://liveviewhero.com",
    description: "Examples and patterns for Phoenix LiveView",
    tags: "elixir,webdev,learning"
  },
  %{
    title: "ElixirConf",
    url: "https://elixirconf.com",
    description: "The premier Elixir conference",
    tags: "elixir,learning,fun"
  },
  %{
    title: "Adopting Elixir",
    url: "https://adoptingelixir.com",
    description: "Strategies for adopting Elixir in your organization",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Erlang Solutions Blog",
    url: "https://www.erlang-solutions.com/blog",
    description: "Blog posts about Erlang and Elixir",
    tags: "elixir,programming,learning"
  },
  %{
    title: "Elixir Radar",
    url: "https://elixirradar.com",
    description: "Weekly Elixir newsletter",
    tags: "elixir,resources,learning"
  },
  %{
    title: "Nerves Project",
    url: "https://nerves-project.org",
    description: "Craft and deploy bulletproof embedded software in Elixir",
    tags: "elixir,tools,devops"
  },
  %{
    title: "GitHub",
    url: "https://github.com",
    description: "Where the world builds software",
    tags: "tools,programming,resources"
  },
  %{
    title: "Stack Overflow",
    url: "https://stackoverflow.com",
    description: "Where developers learn and share knowledge",
    tags: "learning,programming,resources"
  },
  %{
    title: "MDN Web Docs",
    url: "https://developer.mozilla.org",
    description: "Resources for developers, by developers",
    tags: "webdev,learning,resources"
  },
  %{
    title: "CSS-Tricks",
    url: "https://css-tricks.com",
    description: "Tips, Tricks, and Techniques on using CSS",
    tags: "webdev,design,learning"
  },
  %{
    title: "Smashing Magazine",
    url: "https://smashingmagazine.com",
    description: "For web designers and developers",
    tags: "webdev,design,resources"
  },
  %{
    title: "A List Apart",
    url: "https://alistapart.com",
    description: "Articles about web design and development",
    tags: "webdev,design,learning"
  },
  %{
    title: "Frontend Masters",
    url: "https://frontendmasters.com",
    description: "In-depth front-end engineering courses",
    tags: "webdev,learning,resources"
  },
  %{
    title: "JavaScript Weekly",
    url: "https://javascriptweekly.com",
    description: "A weekly JavaScript newsletter",
    tags: "webdev,programming,resources"
  },
  %{
    title: "React Documentation",
    url: "https://react.dev",
    description: "The library for web and native user interfaces",
    tags: "webdev,programming,learning"
  },
  %{
    title: "Vue.js Guide",
    url: "https://vuejs.org/guide",
    description: "The Progressive JavaScript Framework",
    tags: "webdev,programming,learning"
  },
  %{
    title: "Tailwind CSS",
    url: "https://tailwindcss.com",
    description: "A utility-first CSS framework",
    tags: "webdev,design,tools"
  },
  %{
    title: "Docker Hub",
    url: "https://hub.docker.com",
    description: "Container image library",
    tags: "devops,tools,resources"
  },
  %{
    title: "Kubernetes Docs",
    url: "https://kubernetes.io/docs",
    description: "Production-grade container orchestration",
    tags: "devops,learning,resources"
  },
  %{
    title: "AWS Documentation",
    url: "https://docs.aws.amazon.com",
    description: "Amazon Web Services documentation",
    tags: "devops,learning,resources"
  },
  %{
    title: "Terraform by HashiCorp",
    url: "https://terraform.io",
    description: "Infrastructure as code",
    tags: "devops,tools,programming"
  },
  %{
    title: "Ansible Documentation",
    url: "https://docs.ansible.com",
    description: "Automation platform",
    tags: "devops,tools,learning"
  },
  %{
    title: "Prometheus",
    url: "https://prometheus.io",
    description: "Monitoring system and time series database",
    tags: "devops,tools,resources"
  },
  %{
    title: "Grafana Labs",
    url: "https://grafana.com",
    description: "Open source analytics and monitoring",
    tags: "devops,tools,design"
  },
  %{
    title: "CI/CD Pipeline Guide",
    url: "https://about.gitlab.com/topics/ci-cd",
    description: "Everything you need to know about CI/CD",
    tags: "devops,learning,resources"
  },
  %{
    title: "NGINX Documentation",
    url: "https://nginx.org/en/docs",
    description: "High performance web server",
    tags: "devops,webdev,learning"
  },
  %{
    title: "Dribbble",
    url: "https://dribbble.com",
    description: "Discover the world's top designers",
    tags: "design,fun,resources"
  },
  %{
    title: "Behance",
    url: "https://behance.net",
    description: "Creative portfolio platform",
    tags: "design,resources,fun"
  },
  %{
    title: "Figma",
    url: "https://figma.com",
    description: "Collaborative design tool",
    tags: "design,tools,productivity"
  },
  %{
    title: "Awwwards",
    url: "https://awwwards.com",
    description: "The awards of design, creativity and innovation",
    tags: "design,fun,webdev"
  },
  %{
    title: "Land-book",
    url: "https://land-book.com",
    description: "Best landing page design inspiration",
    tags: "design,resources,webdev"
  },
  %{
    title: "UI Patterns",
    url: "https://ui-patterns.com",
    description: "User interface design patterns",
    tags: "design,learning,webdev"
  },
  %{
    title: "Color Hunt",
    url: "https://colorhunt.co",
    description: "Discover beautiful color palettes",
    tags: "design,tools,fun"
  },
  %{
    title: "Coolors",
    url: "https://coolors.co",
    description: "Color scheme generator",
    tags: "design,tools,productivity"
  },
  %{
    title: "Design Systems Gallery",
    url: "https://designsystems.gallery",
    description: "Collection of design systems",
    tags: "design,resources,learning"
  },
  %{
    title: "Refactoring UI",
    url: "https://refactoringui.com",
    description: "Tactics for improving your UI design skills",
    tags: "design,learning,webdev"
  },
  %{
    title: "Coursera",
    url: "https://coursera.org",
    description: "Online courses from top universities",
    tags: "learning,resources,fun"
  },
  %{
    title: "edX",
    url: "https://edx.org",
    description: "Free online courses from top institutions",
    tags: "learning,resources,programming"
  },
  %{
    title: "Udemy",
    url: "https://udemy.com",
    description: "Online learning marketplace",
    tags: "learning,resources,tools"
  },
  %{
    title: "freeCodeCamp",
    url: "https://freecodecamp.org",
    description: "Learn to code for free",
    tags: "learning,programming,resources"
  },
  %{
    title: "Codecademy",
    url: "https://codecademy.com",
    description: "Interactive coding lessons",
    tags: "learning,programming,tools"
  },
  %{
    title: "LeetCode",
    url: "https://leetcode.com",
    description: "Practice coding problems",
    tags: "learning,programming,tools"
  },
  %{
    title: "HackerRank",
    url: "https://hackerrank.com",
    description: "Coding challenges and competitions",
    tags: "learning,programming,fun"
  },
  %{
    title: "Exercism",
    url: "https://exercism.org",
    description: "Code practice and mentorship",
    tags: "learning,programming,resources"
  },
  %{
    title: "Devhints.io",
    url: "https://devhints.io",
    description: "Cheat sheets for developers",
    tags: "learning,resources,productivity"
  },
  %{
    title: "VS Code",
    url: "https://code.visualstudio.com",
    description: "Code editing, redefined",
    tags: "tools,productivity,programming"
  },
  %{
    title: "JetBrains IDEs",
    url: "https://jetbrains.com",
    description: "Professional development tools",
    tags: "tools,productivity,programming"
  },
  %{
    title: "Notion",
    url: "https://notion.so",
    description: "All-in-one workspace",
    tags: "tools,productivity,resources"
  },
  %{
    title: "Linear",
    url: "https://linear.app",
    description: "Issue tracking streamlined",
    tags: "tools,productivity,webdev"
  },
  %{
    title: "Figma Plugins",
    url: "https://figma.com/community/plugins",
    description: "Extend Figma functionality",
    tags: "tools,design,productivity"
  },
  %{
    title: "Postman",
    url: "https://postman.com",
    description: "API development platform",
    tags: "tools,webdev,programming"
  },
  %{
    title: "Insomnia",
    url: "https://insomnia.rest",
    description: "REST and GraphQL client",
    tags: "tools,webdev,productivity"
  },
  %{
    title: "iTerm2",
    url: "https://iterm2.com",
    description: "Terminal for macOS",
    tags: "tools,productivity,devops"
  },
  %{
    title: "Oh My Zsh",
    url: "https://ohmyz.sh",
    description: "Delightful shell framework",
    tags: "tools,productivity,fun"
  },
  %{
    title: "Homebrew",
    url: "https://brew.sh",
    description: "The missing package manager for macOS",
    tags: "tools,devops,productivity"
  },
  %{
    title: "Raycast",
    url: "https://raycast.com",
    description: "Blazingly fast launcher for macOS",
    tags: "tools,productivity,fun"
  },
  %{
    title: "1Password",
    url: "https://1password.com",
    description: "Password manager",
    tags: "tools,productivity,devops"
  },
  %{
    title: "Todoist",
    url: "https://todoist.com",
    description: "To-do list and task manager",
    tags: "productivity,tools,fun"
  },
  %{
    title: "Trello",
    url: "https://trello.com",
    description: "Visual project management",
    tags: "productivity,tools,resources"
  },
  %{
    title: "Asana",
    url: "https://asana.com",
    description: "Work management platform",
    tags: "productivity,tools,learning"
  },
  %{
    title: "Linear Blog",
    url: "https://linear.app/blog",
    description: "Product development insights",
    tags: "productivity,learning,resources"
  },
  %{
    title: "The Pragmatic Programmer",
    url: "https://pragprog.com",
    description: "Books and resources for developers",
    tags: "learning,programming,resources"
  },
  %{
    title: "Hacker News",
    url: "https://news.ycombinator.com",
    description: "Social news for tech enthusiasts",
    tags: "fun,learning,programming"
  },
  %{
    title: "Product Hunt",
    url: "https://producthunt.com",
    description: "Discover new products daily",
    tags: "fun,tools,resources"
  },
  %{
    title: "Indie Hackers",
    url: "https://indiehackers.com",
    description: "Building profitable online businesses",
    tags: "fun,learning,resources"
  },
  %{
    title: "XKCD",
    url: "https://xkcd.com",
    description: "A webcomic of romance, sarcasm, math, and language",
    tags: "fun,programming,resources"
  },
  %{
    title: "CommitStrip",
    url: "https://commitstrip.com",
    description: "Daily life of developers",
    tags: "fun,programming,resources"
  },
  %{
    title: "The Old New Thing",
    url: "https://devblogs.microsoft.com/oldnewthing",
    description: "Raymond Chen's blog",
    tags: "fun,programming,learning"
  },
  %{
    title: "Boring Company FAQ",
    url: "https://boringcompany.com/faq",
    description: "Tunneling technology FAQ",
    tags: "fun,resources,tools"
  },
  %{
    title: "SpaceX News",
    url: "https://spacex.com/news",
    description: "Updates from SpaceX",
    tags: "fun,learning,resources"
  },
  %{
    title: "Dev.to",
    url: "https://dev.to",
    description: "Where programmers share ideas",
    tags: "fun,learning,programming"
  },
  %{
    title: "Medium Tech",
    url: "https://medium.com/topic/technology",
    description: "Technology articles and stories",
    tags: "fun,learning,resources"
  },
  %{
    title: "Quora Programming",
    url: "https://quora.com/topic/Computer-Programming",
    description: "Q&A about programming",
    tags: "fun,learning,programming"
  },
  %{
    title: "Awesome Lists",
    url: "https://github.com/sindresorhus/awesome",
    description: "Curated lists of awesome things",
    tags: "resources,programming,fun"
  },
  %{
    title: "Public APIs",
    url: "https://github.com/public-apis/public-apis",
    description: "A collective list of free APIs",
    tags: "resources,webdev,programming"
  },
  %{
    title: "Free Programming Books",
    url: "https://github.com/EbookFoundation/free-programming-books",
    description: "Free programming books collection",
    tags: "resources,learning,programming"
  },
  %{
    title: "Programming Fonts",
    url: "https://programmingfonts.org",
    description: "Test drive programming fonts",
    tags: "resources,design,tools"
  },
  %{
    title: "DevDocs",
    url: "https://devdocs.io",
    description: "API documentation browser",
    tags: "resources,learning,productivity"
  },
  %{
    title: "Carbon",
    url: "https://carbon.now.sh",
    description: "Create beautiful code snippets",
    tags: "resources,design,fun"
  },
  %{
    title: "Explain Shell",
    url: "https://explainshell.com",
    description: "Explain shell commands",
    tags: "resources,learning,devops"
  },
  %{
    title: "Regex101",
    url: "https://regex101.com",
    description: "Build, test, and debug regex",
    tags: "resources,tools,programming"
  },
  %{
    title: "JSON Formatter",
    url: "https://jsonformatter.org",
    description: "Format and validate JSON",
    tags: "resources,tools,webdev"
  },
  %{
    title: "Cron Expression Generator",
    url: "https://crontab-generator.org",
    description: "Generate cron expressions",
    tags: "resources,tools,devops"
  },
  %{
    title: "What the Diff",
    url: "https://whatthediff.ai",
    description: "AI-powered code review assistant",
    tags: "resources,tools,programming"
  },
  %{
    title: "Elixir Examples",
    url: "https://elixir-examples.github.io",
    description: "Collection of Elixir code examples",
    tags: "elixir,learning,programming"
  },
  %{
    title: "Ecto Query Examples",
    url: "https://hexdocs.pm/ecto/Ecto.Query.html",
    description: "Ecto query documentation",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Oban Pro",
    url: "https://oban.pro",
    description: "Robust job processing for Elixir",
    tags: "elixir,tools,devops"
  },
  %{
    title: "Absinthe GraphQL",
    url: "https://absinthe-graphql.org",
    description: "GraphQL implementation for Elixir",
    tags: "elixir,webdev,programming"
  },
  %{
    title: "Elixir Factory",
    url: "https://elixirfactory.com",
    description: "Elixir conference videos",
    tags: "elixir,learning,fun"
  },
  %{
    title: "Beam Radio",
    url: "https://beamradio.io",
    description: "Podcast about the BEAM ecosystem",
    tags: "elixir,learning,fun"
  },
  %{
    title: "Elixir Wiki",
    url: "https://wiki.elixir-lang.org",
    description: "Community-maintained wiki",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Erlang Documentation",
    url: "https://erlang.org/doc",
    description: "Official Erlang documentation",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Elixir Weekly",
    url: "https://elixirweekly.net",
    description: "Weekly Elixir newsletter",
    tags: "elixir,resources,learning"
  },
  %{
    title: "Thinking Elixir Podcast",
    url: "https://thinkingelixir.com/podcast",
    description: "Podcast about Elixir",
    tags: "elixir,learning,fun"
  },
  %{
    title: "Elixir Circuit",
    url: "https://elixircircuit.com",
    description: "Elixir tutorials and articles",
    tags: "elixir,learning,resources"
  }
]

Enum.each(bookmarks, fn bookmark ->
  Bookmarks.create_bookmark(bookmark)
end)
