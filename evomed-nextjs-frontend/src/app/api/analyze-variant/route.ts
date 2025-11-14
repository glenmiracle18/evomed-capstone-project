import { NextRequest, NextResponse } from "next/server";
import { env } from "~/env";

// Define the request body type
interface VariantAnalysisRequest {
  variant_position: number;
  alternative: string;
  genome: string;
  chromosome: string;
  use_african_adjustment?: boolean;
}

export async function POST(request: NextRequest) {
  try {
    const body: VariantAnalysisRequest = await request.json();

    // Validate required fields
    if (!body.variant_position || !body.alternative || !body.genome || !body.chromosome) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    // Make request to Modal API
    const modalResponse = await fetch(env.NEXT_PUBLIC_ANALYZE_SINGLE_VARIANT_BASE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        variant_position: body.variant_position,
        alternative: body.alternative,
        genome: body.genome,
        chromosome: body.chromosome,
        use_african_adjustment: body.use_african_adjustment ?? true,
      }),
    });

    if (!modalResponse.ok) {
      const errorText = await modalResponse.text();

      if (modalResponse.status === 429) {
        return NextResponse.json(
          { error: "Rate limit exceeded. Please wait a moment and try again." },
          { status: 429 }
        );
      }

      return NextResponse.json(
        { error: `Analysis failed: ${errorText}` },
        { status: modalResponse.status }
      );
    }

    const result = await modalResponse.json();

    // Return the result with CORS headers
    return NextResponse.json(result, {
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });

  } catch (error) {
    console.error("API Error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
    },
  });
}
