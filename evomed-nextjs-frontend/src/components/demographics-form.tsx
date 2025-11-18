"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { User } from "lucide-react";

export interface DemographicsData {
  age: number;
  sex: string;
  ancestry: string;
  personalHistory: {
    hasCancer: boolean;
    cancerType?: string;
    ageAtDiagnosis?: number;
  };
}

interface DemographicsFormProps {
  onUpdate: (data: DemographicsData) => void;
  initialData?: Partial<DemographicsData>;
}

const AFRICAN_ANCESTRIES = [
  { value: "west-african-yoruba", label: "West African - Yoruba (Nigeria)" },
  { value: "west-african-akan", label: "West African - Akan (Ghana)" },
  { value: "west-african-igbo", label: "West African - Igbo (Nigeria)" },
  { value: "west-african-hausa", label: "West African - Hausa (Nigeria/Niger)" },
  { value: "east-african-kikuyu", label: "East African - Kikuyu (Kenya)" },
  { value: "east-african-luo", label: "East African - Luo (Kenya)" },
  { value: "east-african-ethiopian", label: "East African - Ethiopian" },
  { value: "east-african-somali", label: "East African - Somali" },
  { value: "south-african-zulu", label: "South African - Zulu" },
  { value: "south-african-xhosa", label: "South African - Xhosa" },
  { value: "south-african-sotho", label: "South African - Sotho" },
  { value: "central-african-bantu", label: "Central African - Bantu" },
  { value: "north-african-egyptian", label: "North African - Egyptian" },
  { value: "north-african-moroccan", label: "North African - Moroccan" },
  { value: "african-american", label: "African American" },
  { value: "caribbean-african", label: "Caribbean - African Descent" },
  { value: "african-mixed", label: "Mixed African Ancestry" },
  { value: "african-other", label: "Other African Ancestry" },
];

const CANCER_TYPES = [
  "Breast Cancer",
  "Ovarian Cancer",
  "Prostate Cancer",
  "Pancreatic Cancer",
  "Colorectal Cancer",
  "Lung Cancer",
  "Melanoma",
  "Leukemia",
  "Lymphoma",
  "Other Cancer",
];

export function DemographicsForm({
  onUpdate,
  initialData,
}: DemographicsFormProps) {
  const [data, setData] = useState<DemographicsData>({
    age: initialData?.age || 0,
    sex: initialData?.sex || "",
    ancestry: initialData?.ancestry || "",
    personalHistory: initialData?.personalHistory || {
      hasCancer: false,
    },
  });

  const updateData = (field: keyof DemographicsData, value: any) => {
    const updated = { ...data, [field]: value };
    setData(updated);
    onUpdate(updated);
  };

  const updatePersonalHistory = (field: string, value: any) => {
    const updated = {
      ...data,
      personalHistory: {
        ...data.personalHistory,
        [field]: value,
      },
    };
    // Clear cancer details if hasCancer is set to false
    if (field === "hasCancer" && value === false) {
      updated.personalHistory.cancerType = undefined;
      updated.personalHistory.ageAtDiagnosis = undefined;
    }
    setData(updated);
    onUpdate(updated);
  };

  return (
    <Card className="border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-[#3c4f3d] dark:text-white">
          <User className="h-5 w-5" />
          Your Information
        </CardTitle>
        <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
          Provide your demographic information to help us assess your genetic risk.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Age */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
            Age <span className="text-red-500">*</span>
          </label>
          <Input
            type="number"
            min="0"
            max="120"
            placeholder="Enter your age"
            value={data.age || ""}
            onChange={(e) =>
              updateData("age", e.target.value ? parseInt(e.target.value) : 0)
            }
            className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70"
          />
        </div>

        {/* Sex */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
            Sex <span className="text-red-500">*</span>
          </label>
          <Select value={data.sex} onValueChange={(value) => updateData("sex", value)}>
            <SelectTrigger className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70">
              <SelectValue placeholder="Select your sex" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="female">Female</SelectItem>
              <SelectItem value="male">Male</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Ancestry */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
            Ancestry/Ethnicity <span className="text-red-500">*</span>
          </label>
          <Select
            value={data.ancestry}
            onValueChange={(value) => updateData("ancestry", value)}
          >
            <SelectTrigger className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70">
              <SelectValue placeholder="Select your ancestry" />
            </SelectTrigger>
            <SelectContent>
              <div className="px-2 py-1.5 text-xs font-medium text-[#3c4f3d]/50 dark:text-white/50">
                African Populations
              </div>
              {AFRICAN_ANCESTRIES.map((ancestry) => (
                <SelectItem key={ancestry.value} value={ancestry.value}>
                  {ancestry.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="mt-1.5 text-xs text-[#3c4f3d]/50 dark:text-white/50">
            Your ancestry helps us recommend the most relevant genetic variants to test
          </p>
        </div>

        {/* Personal Cancer History */}
        <div className="rounded-lg border border-[#3c4f3d]/10 p-4 dark:border-[#3c4f3d]/20">
          <h4 className="mb-3 text-sm font-medium text-[#3c4f3d] dark:text-white">
            Personal Cancer History
          </h4>

          <div className="space-y-3">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                Have you been diagnosed with cancer?
              </label>
              <Select
                value={data.personalHistory.hasCancer ? "yes" : "no"}
                onValueChange={(value) =>
                  updatePersonalHistory("hasCancer", value === "yes")
                }
              >
                <SelectTrigger className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#242924] dark:text-white/70">
                  <SelectValue placeholder="Select" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="no">No</SelectItem>
                  <SelectItem value="yes">Yes</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {data.personalHistory.hasCancer && (
              <>
                <div>
                  <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                    Type of Cancer
                  </label>
                  <Select
                    value={data.personalHistory.cancerType || ""}
                    onValueChange={(value) =>
                      updatePersonalHistory("cancerType", value)
                    }
                  >
                    <SelectTrigger className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#242924] dark:text-white/70">
                      <SelectValue placeholder="Select cancer type" />
                    </SelectTrigger>
                    <SelectContent>
                      {CANCER_TYPES.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                    Age at Diagnosis (optional)
                  </label>
                  <Input
                    type="number"
                    min="0"
                    max="120"
                    placeholder="e.g., 45"
                    value={data.personalHistory.ageAtDiagnosis || ""}
                    onChange={(e) =>
                      updatePersonalHistory(
                        "ageAtDiagnosis",
                        e.target.value ? parseInt(e.target.value) : undefined
                      )
                    }
                    className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#242924] dark:text-white/70"
                  />
                </div>
              </>
            )}
          </div>
        </div>

        <div className="rounded-lg bg-amber-50 p-3 dark:bg-amber-950/20">
          <p className="text-xs text-amber-900 dark:text-amber-200">
            <strong>Privacy Notice:</strong> All information is processed locally
            and used only to generate personalized recommendations. Your data is
            never stored or shared.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
