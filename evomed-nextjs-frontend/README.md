# EvoMed Next.js Frontend

This is the frontend application for the EvoMed platform, a tool for genetic variant analysis and hereditary cancer pre-screening. It provides a user-friendly interface for interacting with the variant analysis models and viewing results.

## Features

-   **Pre-Screening Questionnaire:** A multi-step form to gather demographic and family history data for risk assessment.
-   **Genetic Analysis:** Tools for analyzing and visualizing genetic variants.
-   **Risk Assessment:** Displays personalized risk assessments and testing recommendations.
-   **Secure Authentication:** User accounts and authentication are handled using Clerk.

## Tech Stack

-   [Next.js](https://nextjs.org) - React Framework
-   [TypeScript](https://www.typescriptlang.org/) - Typed JavaScript
-   [Tailwind CSS](https://tailwindcss.com) - Utility-First CSS Framework
-   [Shadcn/ui](https://ui.shadcn.com/) - Re-usable components built using Radix UI and Tailwind CSS.
-   [Clerk](https://clerk.com/) - User Authentication and Management

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

-   Node.js (v20.x or later recommended)
-   npm

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/variant-analysis-evo2.git
    ```

2.  **Navigate to the frontend directory:**
    ```bash
    cd variant-analysis-evo2/evomed-nextjs-frontend
    ```

3.  **Install dependencies:**
    ```bash
    npm install
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the `evomed-nextjs-frontend` directory by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Update the `.env` file with your credentials and API endpoints:
    -   `CLERK_SECRET_KEY`: Your secret key from the Clerk dashboard.
    -   `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: Your publishable key from the Clerk dashboard.
    -   `NEXT_PUBLIC_ANALYZE_SINGLE_VARIANT_BASE_URL`: The base URL for the backend analysis API.

### Running the Development Server

Once the installation is complete, you can start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

## Available Scripts

-   `npm run dev`: Starts the development server with hot-reloading.
-   `npm run build`: Builds the application for production.
-   `npm run start`: Starts a production server.
-   `npm run lint`: Lints the codebase using Next.js' built-in ESLint configuration.
-   `npm run format:check`: Checks for formatting issues using Prettier.

## Deployment

The easiest way to deploy this Next.js application is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme).

Check out the [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.