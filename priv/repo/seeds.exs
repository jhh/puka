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

alias Puka.Repo
alias Puka.Bookmarks.Bookmark
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

# Create 100 bookmarks with varying description lengths and spaced timestamps
bookmarks = [
  %{
    title: "Elixir School",
    url: "https://elixirschool.com",
    description:
      "Elixir School is an open-source learning platform dedicated to teaching the Elixir programming language. It offers comprehensive lessons covering everything from basic syntax to advanced concepts like metaprogramming and OTP. The curriculum is designed for developers of all skill levels, whether you're coming from another programming language or starting fresh. Each lesson includes practical examples and exercises to reinforce your understanding of Elixir's functional programming paradigm.",
    tags: "elixir,learning,programming"
  },
  %{
    title: "Hex Docs",
    url: "https://hexdocs.pm",
    description:
      "Hex Docs serves as the official documentation repository for all packages published on Hex.pm, Elixir's package manager. Developers can search and browse detailed API documentation for thousands of open-source libraries. The site provides version-specific documentation, making it easy to find information relevant to the exact version you're using in your project. It's an indispensable resource for Elixir developers integrating third-party packages.",
    tags: "elixir,resources,programming"
  },
  %{
    title: "Elixir Forum",
    url: "https://elixirforum.com",
    description:
      "A welcoming community forum where Elixir developers discuss best practices, share libraries, and help each other solve problems.",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Phoenix Framework",
    url: "https://phoenixframework.org",
    description:
      "Phoenix is a modern web framework built with Elixir that emphasizes productivity, reliability, and performance. It leverages the Erlang VM's capabilities to support millions of concurrent connections, making it ideal for real-time applications. The framework comes with built-in features like channels for WebSocket support, a robust router, and an elegant ORM in Ecto. Phoenix enables developers to build scalable, maintainable web applications with less boilerplate code.",
    tags: "elixir,webdev,programming"
  },
  %{
    title: "LiveView Hero",
    url: "https://liveviewhero.com",
    description:
      "LiveView Hero provides real-world examples and design patterns for building interactive applications with Phoenix LiveView.",
    tags: "elixir,webdev,learning"
  },
  %{
    title: "ElixirConf",
    url: "https://elixirconf.com",
    description:
      "The premier annual conference bringing together Elixir enthusiasts from around the world. Attendees can watch keynote presentations, participate in workshops, and network with industry leaders who are pushing the boundaries of what's possible with Elixir and the BEAM virtual machine.",
    tags: "elixir,learning,fun"
  },
  %{
    title: "Adopting Elixir",
    url: "https://adoptingelixir.com",
    description:
      "Adopting Elixir provides organizations with practical strategies for introducing Elixir into their technology stack. The resource covers everything from building a business case and training existing developers to migrating systems incrementally. It addresses common concerns about adopting a relatively new language and provides real-world success stories from companies that have made the transition.",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Erlang Solutions Blog",
    url: "https://www.erlang-solutions.com/blog",
    description: "Technical articles about Erlang and Elixir development.",
    tags: "elixir,programming,learning"
  },
  %{
    title: "Elixir Radar",
    url: "https://elixirradar.com",
    description:
      "A weekly newsletter curating the best Elixir articles, libraries, and community updates.",
    tags: "elixir,resources,learning"
  },
  %{
    title: "Nerves Project",
    url: "https://nerves-project.org",
    description:
      "Nerves is a framework for building embedded systems using Elixir, enabling developers to create robust IoT devices with familiar tools.",
    tags: "elixir,tools,devops"
  },
  %{
    title: "GitHub",
    url: "https://github.com",
    description:
      "GitHub is the world's largest platform for software development and version control. It hosts millions of open-source and private repositories, providing tools for code review, project management, and continuous integration. Developers use GitHub to collaborate on code, track issues, and deploy applications. The platform supports Git repositories and offers features like GitHub Actions for automation, GitHub Pages for hosting, and a rich ecosystem of third-party integrations.",
    tags: "tools,programming,resources"
  },
  %{
    title: "Stack Overflow",
    url: "https://stackoverflow.com",
    description: "The go-to Q&A site where developers help each other with coding challenges.",
    tags: "learning,programming,resources"
  },
  %{
    title: "MDN Web Docs",
    url: "https://developer.mozilla.org",
    description:
      "Mozilla's comprehensive documentation covers HTML, CSS, JavaScript, and web APIs with detailed explanations and interactive examples.",
    tags: "webdev,learning,resources"
  },
  %{
    title: "CSS-Tricks",
    url: "https://css-tricks.com",
    description:
      "CSS-Tricks has been a leading resource for web designers and frontend developers since 2007. The site publishes daily articles covering everything from CSS fundamentals to advanced layout techniques like Grid and Flexbox. You'll find tutorials on responsive design, accessibility, performance optimization, and modern CSS features. The site also includes an extensive almanac documenting CSS properties and selectors with practical examples.",
    tags: "webdev,design,learning"
  },
  %{
    title: "Smashing Magazine",
    url: "https://smashingmagazine.com",
    description:
      "Smashing Magazine delivers reliable, useful, but most importantly practical articles for web designers and developers. They publish in-depth guides on frontend development, UX design, and web performance. The magazine also hosts conferences and workshops worldwide, bringing the community together to learn and share knowledge.",
    tags: "webdev,design,resources"
  },
  %{
    title: "A List Apart",
    url: "https://alistapart.com",
    description:
      "Explores the design, development, and meaning of web content with a focus on web standards and best practices.",
    tags: "webdev,design,learning"
  },
  %{
    title: "Frontend Masters",
    url: "https://frontendmasters.com",
    description: "Offers expert-led video courses on modern frontend technologies.",
    tags: "webdev,learning,resources"
  },
  %{
    title: "JavaScript Weekly",
    url: "https://javascriptweekly.com",
    description:
      "A curated newsletter keeping JavaScript developers up-to-date with the latest news, libraries, and techniques in the ecosystem.",
    tags: "webdev,programming,resources"
  },
  %{
    title: "React Documentation",
    url: "https://react.dev",
    description:
      "The official React documentation has been completely rewritten with a focus on learning by doing. It teaches modern React patterns including hooks, suspense, and concurrent features. The new docs include interactive code examples that you can edit and run directly in your browser. Whether you're learning React for the first time or upgrading your knowledge, this resource provides the definitive guide to building user interfaces with React.",
    tags: "webdev,programming,learning"
  },
  %{
    title: "Vue.js Guide",
    url: "https://vuejs.org/guide",
    description: "Learn Vue.js, the approachable frontend framework.",
    tags: "webdev,programming,learning"
  },
  %{
    title: "Tailwind CSS",
    url: "https://tailwindcss.com",
    description:
      "Tailwind CSS revolutionizes how developers write styles by providing a utility-first approach. Instead of writing custom CSS, you compose designs using pre-built utility classes directly in your HTML. This methodology leads to faster development, smaller CSS bundles, and more consistent designs across projects. The framework is highly customizable through its configuration file and includes features like responsive prefixes, dark mode support, and JIT compilation for optimal performance.",
    tags: "webdev,design,tools"
  },
  %{
    title: "Docker Hub",
    url: "https://hub.docker.com",
    description: "The world's largest library of container images.",
    tags: "devops,tools,resources"
  },
  %{
    title: "Kubernetes Docs",
    url: "https://kubernetes.io/docs",
    description: "Official documentation for orchestrating containers at scale.",
    tags: "devops,learning,resources"
  },
  %{
    title: "AWS Documentation",
    url: "https://docs.aws.amazon.com",
    description:
      "Comprehensive guides for Amazon Web Services including compute, storage, database, and machine learning services. The documentation includes getting started tutorials, API references, architectural best practices, and troubleshooting guides. Whether you're deploying a simple web application or designing a complex multi-region architecture, AWS docs provide the information needed to leverage cloud services effectively.",
    tags: "devops,learning,resources"
  },
  %{
    title: "Terraform by HashiCorp",
    url: "https://terraform.io",
    description: "Infrastructure as code for cloud provisioning.",
    tags: "devops,tools,programming"
  },
  %{
    title: "Ansible Documentation",
    url: "https://docs.ansible.com",
    description:
      "Learn how to automate IT infrastructure with Ansible's simple yet powerful automation platform.",
    tags: "devops,tools,learning"
  },
  %{
    title: "Prometheus",
    url: "https://prometheus.io",
    description:
      "An open-source monitoring solution that collects metrics from configured targets at given intervals, evaluates rule expressions, displays results, and can trigger alerts.",
    tags: "devops,tools,resources"
  },
  %{
    title: "Grafana Labs",
    url: "https://grafana.com",
    description:
      "Grafana Labs develops Grafana, the leading open-source platform for monitoring and observability. It allows you to query, visualize, alert on, and understand your metrics no matter where they are stored. Create beautiful dashboards with rich visualizations and share them with your team. Grafana integrates with Prometheus, InfluxDB, Elasticsearch, and many other data sources.",
    tags: "devops,tools,design"
  },
  %{
    title: "CI/CD Pipeline Guide",
    url: "https://about.gitlab.com/topics/ci-cd",
    description:
      "GitLab's comprehensive guide covers everything about Continuous Integration and Continuous Deployment. Learn how to automate your software delivery pipeline.",
    tags: "devops,learning,resources"
  },
  %{
    title: "NGINX Documentation",
    url: "https://nginx.org/en/docs",
    description: "Official docs for the high-performance web server and reverse proxy.",
    tags: "devops,webdev,learning"
  },
  %{
    title: "Dribbble",
    url: "https://dribbble.com",
    description:
      "Dribbble is where designers gain inspiration, feedback, community, and jobs. It serves as a self-promotion and networking platform for graphic design, web design, illustration, photography, and other creative areas. Designers share small screenshots of their work, process, and projects. It's an excellent resource for staying current with design trends and discovering talented designers for your projects.",
    tags: "design,fun,resources"
  },
  %{
    title: "Behance",
    url: "https://behance.net",
    description: "Adobe's creative portfolio platform.",
    tags: "design,resources,fun"
  },
  %{
    title: "Figma",
    url: "https://figma.com",
    description:
      "Figma has transformed how teams design by bringing collaboration directly into the design tool. Multiple team members can work on the same file simultaneously, seeing each other's cursors and changes in real-time. The platform includes prototyping capabilities, design systems management, and developer handoff features. With FigJam, teams can also collaborate on whiteboarding sessions. Figma runs entirely in the browser, making it accessible across all operating systems without installations.",
    tags: "design,tools,productivity"
  },
  %{
    title: "Awwwards",
    url: "https://awwwards.com",
    description: "Recognizing the talent and effort of the world's best web designers.",
    tags: "design,fun,webdev"
  },
  %{
    title: "Land-book",
    url: "https://land-book.com",
    description: "A curated gallery of the best landing page design inspiration.",
    tags: "design,resources,webdev"
  },
  %{
    title: "UI Patterns",
    url: "https://ui-patterns.com",
    description:
      "A collection of user interface design patterns to help you solve common design problems.",
    tags: "design,learning,webdev"
  },
  %{
    title: "Color Hunt",
    url: "https://colorhunt.co",
    description: "Discover thousands of beautiful color palettes for your design projects.",
    tags: "design,tools,fun"
  },
  %{
    title: "Coolors",
    url: "https://coolors.co",
    description:
      "Coolors is a super-fast color scheme generator that helps designers create perfect palettes in seconds. Generate color schemes from images, lock colors you like, and export in multiple formats including CSS, SVG, and PDF. The tool also includes accessibility features to check contrast ratios and color blindness simulations. Whether you're starting from scratch or refining an existing palette, Coolors streamlines your color selection workflow.",
    tags: "design,tools,productivity"
  },
  %{
    title: "Design Systems Gallery",
    url: "https://designsystems.gallery",
    description: "Explore how leading companies structure and document their design systems.",
    tags: "design,resources,learning"
  },
  %{
    title: "Refactoring UI",
    url: "https://refactoringui.com",
    description: "Learn practical tactics for creating beautiful user interfaces.",
    tags: "design,learning,webdev"
  },
  %{
    title: "Coursera",
    url: "https://coursera.org",
    description:
      "Coursera partners with over 200 leading universities and companies to bring flexible, affordable, job-relevant online learning to individuals and organizations worldwide. They offer a wide range of learning opportunities—from hands-on projects and courses to job-ready certificates and degree programs. Whether you want to start a new career or advance in your current one, Coursera provides courses in data science, computer science, business, and more.",
    tags: "learning,resources,fun"
  },
  %{
    title: "edX",
    url: "https://edx.org",
    description: "Access free online courses from Harvard, MIT, and other top institutions.",
    tags: "learning,resources,programming"
  },
  %{
    title: "Udemy",
    url: "https://udemy.com",
    description:
      "An online learning marketplace with over 150,000 courses on every topic imaginable.",
    tags: "learning,resources,tools"
  },
  %{
    title: "freeCodeCamp",
    url: "https://freecodecamp.org",
    description:
      "Learn to code for free through an interactive curriculum and build projects for nonprofits.",
    tags: "learning,programming,resources"
  },
  %{
    title: "Codecademy",
    url: "https://codecademy.com",
    description:
      "Codecademy offers interactive coding lessons that make learning programming accessible and engaging. Their hands-on approach lets you write code directly in the browser while receiving immediate feedback. The platform covers languages like Python, JavaScript, Ruby, and more, with structured career paths for frontend, backend, and full-stack development. They also offer Pro features including real-world projects, quizzes, and certificates of completion.",
    tags: "learning,programming,tools"
  },
  %{
    title: "LeetCode",
    url: "https://leetcode.com",
    description: "Practice coding problems to prepare for technical interviews.",
    tags: "learning,programming,tools"
  },
  %{
    title: "HackerRank",
    url: "https://hackerrank.com",
    description: "Compete in coding challenges and build your developer profile.",
    tags: "learning,programming,fun"
  },
  %{
    title: "Exercism",
    url: "https://exercism.org",
    description: "Free coding practice and mentorship across 60+ programming languages.",
    tags: "learning,programming,resources"
  },
  %{
    title: "Devhints.io",
    url: "https://devhints.io",
    description:
      "A collection of cheat sheets for developers covering various technologies and tools.",
    tags: "learning,resources,productivity"
  },
  %{
    title: "VS Code",
    url: "https://code.visualstudio.com",
    description:
      "Visual Studio Code is a lightweight but powerful source code editor that runs on your desktop and is available for Windows, macOS, and Linux. It comes with built-in support for JavaScript, TypeScript, and Node.js, and has a rich ecosystem of extensions for other languages and runtimes. Features include IntelliSense code completion, debugging, built-in Git support, and customizable themes and keyboard shortcuts.",
    tags: "tools,productivity,programming"
  },
  %{
    title: "JetBrains IDEs",
    url: "https://jetbrains.com",
    description: "Professional development environments for various languages.",
    tags: "tools,productivity,programming"
  },
  %{
    title: "Notion",
    url: "https://notion.so",
    description:
      "Notion provides an all-in-one workspace where you can write, plan, collaborate, and get organized. It combines the functionality of note-taking apps, project management tools, wikis, and databases into a single flexible platform. Create rich documents with embedded media, build custom databases with multiple views, and collaborate with your team in real-time. The tool adapts to your workflow, whether you're managing personal tasks or coordinating complex team projects.",
    tags: "tools,productivity,resources"
  },
  %{
    title: "Linear",
    url: "https://linear.app",
    description: "The issue tracking tool that helps teams build software faster.",
    tags: "tools,productivity,webdev"
  },
  %{
    title: "Figma Plugins",
    url: "https://figma.com/community/plugins",
    description: "Extend Figma's functionality with thousands of community-created plugins.",
    tags: "tools,design,productivity"
  },
  %{
    title: "Postman",
    url: "https://postman.com",
    description:
      "Postman simplifies API development for developers by providing tools to build, test, and modify APIs. It offers an intuitive interface for sending HTTP requests, organizing collections of endpoints, and automating tests. Developers can mock servers, generate documentation, and collaborate with team members through workspaces. Postman supports REST, SOAP, GraphQL, and WebSocket protocols, making it a versatile tool for any API workflow.",
    tags: "tools,webdev,programming"
  },
  %{
    title: "Insomnia",
    url: "https://insomnia.rest",
    description: "A powerful REST and GraphQL client with a clean interface.",
    tags: "tools,webdev,productivity"
  },
  %{
    title: "iTerm2",
    url: "https://iterm2.com",
    description: "The popular terminal emulator for macOS packed with features.",
    tags: "tools,productivity,devops"
  },
  %{
    title: "Oh My Zsh",
    url: "https://ohmyz.sh",
    description:
      "A delightful, open-source framework for managing your Zsh configuration with hundreds of plugins and themes.",
    tags: "tools,productivity,fun"
  },
  %{
    title: "Homebrew",
    url: "https://brew.sh",
    description:
      "Homebrew is the missing package manager for macOS (and Linux). It simplifies the installation of software and tools that Apple didn't provide. With a simple command, you can install thousands of open-source packages, programming languages, and applications. Homebrew handles dependencies automatically and keeps everything organized in a central location, making it easy to manage your development environment.",
    tags: "tools,devops,productivity"
  },
  %{
    title: "Raycast",
    url: "https://raycast.com",
    description: "Blazingly fast, totally extendable launcher for macOS.",
    tags: "tools,productivity,fun"
  },
  %{
    title: "1Password",
    url: "https://1password.com",
    description: "Secure password manager for individuals, families, and businesses.",
    tags: "tools,productivity,devops"
  },
  %{
    title: "Todoist",
    url: "https://todoist.com",
    description:
      "Todoist is a task management application that helps millions of people organize work and life. It features natural language processing for quick task entry, projects and sub-projects for organization, priority levels, and collaboration features. The app works across all devices with seamless synchronization, and integrates with hundreds of other tools. Whether managing simple to-do lists or complex projects, Todoist adapts to your workflow.",
    tags: "productivity,tools,fun"
  },
  %{
    title: "Trello",
    url: "https://trello.com",
    description: "Visual project management using Kanban boards.",
    tags: "productivity,tools,resources"
  },
  %{
    title: "Asana",
    url: "https://asana.com",
    description: "Work management platform for teams to organize, track, and manage work.",
    tags: "productivity,tools,learning"
  },
  %{
    title: "Linear Blog",
    url: "https://linear.app/blog",
    description: "Insights on building products and leading engineering teams.",
    tags: "productivity,learning,resources"
  },
  %{
    title: "The Pragmatic Programmer",
    url: "https://pragprog.com",
    description:
      "The Pragmatic Bookshelf publishes books and resources for software developers created by working practitioners. Their catalog includes classics like \"The Pragmatic Programmer\" along with modern guides on emerging technologies. They focus on practical, hands-on learning with real-world examples. The site also offers screencasts, workshops, and articles to help developers stay current with industry best practices.",
    tags: "learning,programming,resources"
  },
  %{
    title: "Hacker News",
    url: "https://news.ycombinator.com",
    description: "Tech news aggregator run by Y Combinator.",
    tags: "fun,learning,programming"
  },
  %{
    title: "Product Hunt",
    url: "https://producthunt.com",
    description: "Discover the latest apps, websites, and tech products every day.",
    tags: "fun,tools,resources"
  },
  %{
    title: "Indie Hackers",
    url: "https://indiehackers.com",
    description: "A community for entrepreneurs building profitable online businesses.",
    tags: "fun,learning,resources"
  },
  %{
    title: "XKCD",
    url: "https://xkcd.com",
    description:
      "XKCD is a webcomic of romance, sarcasm, math, and language created by Randall Munroe. It features stick-figure drawings with witty commentary on science, technology, mathematics, and relationships. The comics often include elaborate infographics and visualizations that make complex topics accessible. It's a beloved resource in the programming community for its humorous takes on technical topics.",
    tags: "fun,programming,resources"
  },
  %{
    title: "CommitStrip",
    url: "https://commitstrip.com",
    description: "Comics about the daily life of developers.",
    tags: "fun,programming,resources"
  },
  %{
    title: "The Old New Thing",
    url: "https://devblogs.microsoft.com/oldnewthing",
    description: "Raymond Chen's blog about Windows history and programming.",
    tags: "fun,programming,learning"
  },
  %{
    title: "Boring Company FAQ",
    url: "https://boringcompany.com/faq",
    description:
      "Learn about Elon Musk's tunnel construction company and their vision for underground transportation.",
    tags: "fun,resources,tools"
  },
  %{
    title: "SpaceX News",
    url: "https://spacex.com/news",
    description: "Latest updates on rocket launches and space exploration from SpaceX.",
    tags: "fun,learning,resources"
  },
  %{
    title: "Dev.to",
    url: "https://dev.to",
    description:
      "DEV Community is a constructive and inclusive social network for software developers. With you every step of your journey, the platform enables developers to share knowledge, ask questions, and connect with peers. Articles cover every programming language, framework, and career topic imaginable. The community-driven nature ensures diverse perspectives and practical advice from developers at all levels.",
    tags: "fun,learning,programming"
  },
  %{
    title: "Medium Tech",
    url: "https://medium.com/topic/technology",
    description: "Technology articles and stories from writers worldwide.",
    tags: "fun,learning,resources"
  },
  %{
    title: "Quora Programming",
    url: "https://quora.com/topic/Computer-Programming",
    description: "Q&A community for programming questions.",
    tags: "fun,learning,programming"
  },
  %{
    title: "Awesome Lists",
    url: "https://github.com/sindresorhus/awesome",
    description:
      "Awesome lists curate the best resources for various topics, from programming languages to hardware. They are community-maintained collections that help developers discover high-quality libraries, tools, and learning resources. Whether you're looking for React components, Python frameworks, or DevOps tools, there's likely an awesome list for it.",
    tags: "resources,programming,fun"
  },
  %{
    title: "Public APIs",
    url: "https://github.com/public-apis/public-apis",
    description: "A collective list of free APIs for use in software development.",
    tags: "resources,webdev,programming"
  },
  %{
    title: "Free Programming Books",
    url: "https://github.com/EbookFoundation/free-programming-books",
    description: "Freely available programming books in many languages.",
    tags: "resources,learning,programming"
  },
  %{
    title: "Programming Fonts",
    url: "https://programmingfonts.org",
    description: "Test drive programming fonts with your own code.",
    tags: "resources,design,tools"
  },
  %{
    title: "DevDocs",
    url: "https://devdocs.io",
    description:
      "DevDocs is an open-source API documentation browser that combines multiple documentation sets in a fast, organized, and searchable interface. It works offline once loaded, making it perfect for coding on planes or anywhere without internet. The interface is clean and keyboard-friendly, with features like fuzzy search, deep linking, and instant search. Developers can customize which documentation sets to include and organize them by category.",
    tags: "resources,learning,productivity"
  },
  %{
    title: "Carbon",
    url: "https://carbon.now.sh",
    description: "Create and share beautiful images of your source code.",
    tags: "resources,design,fun"
  },
  %{
    title: "Explain Shell",
    url: "https://explainshell.com",
    description: "Type in a shell command and see what each part does.",
    tags: "resources,learning,devops"
  },
  %{
    title: "Regex101",
    url: "https://regex101.com",
    description: "Build, test, and debug regular expressions with detailed explanation.",
    tags: "resources,tools,programming"
  },
  %{
    title: "JSON Formatter",
    url: "https://jsonformatter.org",
    description: "Format and validate JSON data online.",
    tags: "resources,tools,webdev"
  },
  %{
    title: "Cron Expression Generator",
    url: "https://crontab-generator.org",
    description: "Easily generate cron expressions for scheduling tasks.",
    tags: "resources,tools,devops"
  },
  %{
    title: "What the Diff",
    url: "https://whatthediff.ai",
    description: "AI-powered code review assistant.",
    tags: "resources,tools,programming"
  },
  %{
    title: "Elixir Examples",
    url: "https://elixir-examples.github.io",
    description:
      "Elixir Examples is a community-driven collection of practical Elixir code snippets and demonstrations. The site organizes examples by topic, making it easy to find patterns for common tasks like working with collections, handling strings, or implementing OTP behaviors. Each example includes runnable code and explanations. It's a great resource for learning idiomatic Elixir and discovering lesser-known language features.",
    tags: "elixir,learning,programming"
  },
  %{
    title: "Ecto Query Examples",
    url: "https://hexdocs.pm/ecto/Ecto.Query.html",
    description: "Official Ecto query documentation and examples.",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Oban Pro",
    url: "https://oban.pro",
    description:
      "Oban provides robust job processing for Elixir applications with persistence, reliability, and observability built-in.",
    tags: "elixir,tools,devops"
  },
  %{
    title: "Absinthe GraphQL",
    url: "https://absinthe-graphql.org",
    description:
      "Absinthe is the GraphQL toolkit for Elixir, providing the means to build flexible, extensible, and robust GraphQL APIs.",
    tags: "elixir,webdev,programming"
  },
  %{
    title: "Elixir Factory",
    url: "https://elixirfactory.com",
    description: "Watch talks and presentations from Elixir conferences.",
    tags: "elixir,learning,fun"
  },
  %{
    title: "Beam Radio",
    url: "https://beamradio.io",
    description: "A podcast about the BEAM ecosystem including Elixir, Erlang, and LFE.",
    tags: "elixir,learning,fun"
  },
  %{
    title: "Elixir Wiki",
    url: "https://wiki.elixir-lang.org",
    description: "Community-maintained wiki with comprehensive information about Elixir.",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Erlang Documentation",
    url: "https://erlang.org/doc",
    description:
      "The official Erlang documentation provides comprehensive coverage of the Erlang programming language and runtime environment. It includes reference manuals, user guides, and tutorials covering OTP behaviors, distributed computing, and fault-tolerant system design. Since Elixir runs on the Erlang VM, understanding Erlang documentation is valuable for advanced Elixir development. The docs explain the foundational concepts that make the BEAM ecosystem unique.",
    tags: "elixir,learning,resources"
  },
  %{
    title: "Elixir Weekly",
    url: "https://elixirweekly.net",
    description: "A curated newsletter covering the latest in the Elixir ecosystem.",
    tags: "elixir,resources,learning"
  },
  %{
    title: "Thinking Elixir Podcast",
    url: "https://thinkingelixir.com/podcast",
    description: "Conversations with Elixir developers about their experiences and insights.",
    tags: "elixir,learning,fun"
  },
  %{
    title: "Elixir Circuit",
    url: "https://elixircircuit.com",
    description: "Tutorials and articles for Elixir developers of all skill levels.",
    tags: "elixir,learning,resources"
  }
]

# Insert bookmarks with spaced timestamps (2 seconds apart)
# to ensure consistent sorting

# Clear existing bookmarks and their tag associations first
Repo.delete_all("bookmarks_tags")
Repo.delete_all(Bookmark)

now = DateTime.utc_now() |> DateTime.truncate(:second)

Enum.with_index(bookmarks)
|> Enum.each(fn {bookmark, index} ->
  # Calculate timestamp 2 seconds apart for each bookmark
  inserted_at = DateTime.add(now, -(index * 2), :second)

  # Parse tags
  tag_list = bookmark.tags |> String.split(",") |> Enum.map(&String.trim/1)

  tags_to_assoc =
    Enum.map(tag_list, fn name ->
      Repo.get_by!(Puka.Tags.Tag, name: name)
    end)

  # Insert bookmark first (Ecto will set timestamps automatically)
  {:ok, inserted_bookmark} =
    %Bookmark{}
    |> Bookmark.changeset(%{
      title: bookmark.title,
      url: bookmark.url,
      description: bookmark.description
    })
    |> Ecto.Changeset.put_assoc(:tags, tags_to_assoc)
    |> Repo.insert()

  # Update timestamps manually after insertion
  inserted_bookmark
  |> Ecto.Changeset.change(
    inserted_at: inserted_at,
    updated_at: inserted_at
  )
  |> Repo.update!()
end)

IO.puts("Seeded #{length(bookmarks)} bookmarks with spaced timestamps")
