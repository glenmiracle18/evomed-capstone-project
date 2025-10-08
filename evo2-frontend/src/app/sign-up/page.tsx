import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-black">
      <SignUp
        appearance={{
          baseTheme: "dark",
          elements: {
            rootBox: "mx-auto",
            card: "bg-gray-900 border border-gray-700",
            headerTitle: "text-white",
            headerSubtitle: "text-gray-300",
            socialButtonsBlockButton: "border-gray-600 text-white hover:bg-gray-800",
            formFieldLabel: "text-gray-300",
            formFieldInput: "bg-gray-800 border-gray-600 text-white",
            footerActionText: "text-gray-400",
            footerActionLink: "text-white hover:text-gray-300",
            formButtonPrimary: "bg-white text-black hover:bg-gray-200",
          },
        }}
        redirectUrl="/app"
      />
    </div>
  );
}