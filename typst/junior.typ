// Example for a junior engineer: no summary, projects carry weight, one page.
// Ana Petrović and every company here are made up.
// Compile: typst compile --font-path ../fonts junior.typ
#import "lib.typ": *

#show: resume.with(
  name: "Ana Petrović",
  contact: (
    [Novi Sad, Serbia],
    link("mailto:ana@example.com")[ana\@example.com],
    [+381 64 000 0000],
    link("https://www.linkedin.com/in/ana-example")[linkedin.com/in/ana-example],
    link("https://github.com/ana-example")[github.com/ana-example],
  ),
  headline: "Junior Backend Engineer",
  tagline: "Builds and tests .NET APIs; shipped two production services in her first year",
  keywords: ("Junior Backend Engineer", "C#", ".NET", "ASP.NET Core", "PostgreSQL"),
)

= Skills
#skills(
  [C\#, .NET 8, ASP.NET Core],
  [PostgreSQL, Entity Framework Core],
  [REST API design],
  [xUnit, Testcontainers],
  [Docker, GitHub Actions],
  [Azure App Service],
  [Git],
)

= Professional Experience

#job("Brightline Software d.o.o.", title: "Junior Software Engineer", location: "Novi Sad, Serbia", dates: "Sep 2024 – Present")[
  - Built a shipment-tracking API in ASP.NET Core that serves 1,200 requests per minute at 120 ms p95.
  - Cut the test suite from 14 to 5 minutes by moving integration tests to Testcontainers.
  - Fixed 40+ production bugs from the support queue and wrote the runbook the on-call team now uses.
  - Shipped a second service, invoice export, from design review to production in six weeks.
]

#job("Datalab Systems d.o.o.", title: "Software Engineering Intern", location: "Novi Sad, Serbia", dates: "Feb 2024 – Jul 2024")[
  - Added CSV and Excel export to an internal reporting tool used by 300 employees.
  - Wrote 120 unit tests, raising coverage of the billing module from 35% to 78%.
]

= Selected Projects

#project(
  "Budget Buddy",
  info: link("https://github.com/ana-example/budget-buddy")[github.com/ana-example/budget-buddy],
  stack: "C#, Blazor, SQLite",
)[
  - Personal finance tracker with bank CSV import; 40 GitHub stars and 6 outside contributors.
]

#project("Open-source contributions", stack: "C#")[
  - Two merged pull requests to an open-source .NET logging library: a date-formatting fix and its docs.
]

= Education
- #education("B.Sc. in Software Engineering", school: "University of Novi Sad", year: "2024 (GPA 9.1/10)")

= Certifications
#inline[Microsoft Certified: Azure Fundamentals (AZ-900)]

= Languages
#inline[Serbian (native)][English (C1)]
