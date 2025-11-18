"use client";

import { useState } from "react";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { Plus, Trash2, Users } from "lucide-react";

export interface FamilyMember {
  id: string;
  relationship: string;
  hasCancer: boolean;
  cancerType?: string;
  ageAtDiagnosis?: number;
}

interface FamilyHistoryQuestionnaireProps {
  onUpdate: (familyMembers: FamilyMember[]) => void;
  initialData?: FamilyMember[];
}

const RELATIONSHIPS = [
  { value: "mother", label: "Mother" },
  { value: "father", label: "Father" },
  { value: "sister", label: "Sister" },
  { value: "brother", label: "Brother" },
  { value: "daughter", label: "Daughter" },
  { value: "son", label: "Son" },
  { value: "grandmother", label: "Grandmother" },
  { value: "grandfather", label: "Grandfather" },
  { value: "aunt", label: "Aunt" },
  { value: "uncle", label: "Uncle" },
  { value: "niece", label: "Niece" },
  { value: "nephew", label: "Nephew" },
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

export function FamilyHistoryQuestionnaire({
  onUpdate,
  initialData = [],
}: FamilyHistoryQuestionnaireProps) {
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>(
    initialData.length > 0 ? initialData : []
  );

  const addFamilyMember = () => {
    const newMember: FamilyMember = {
      id: Date.now().toString(),
      relationship: "",
      hasCancer: false,
    };
    const updated = [...familyMembers, newMember];
    setFamilyMembers(updated);
    onUpdate(updated);
  };

  const removeFamilyMember = (id: string) => {
    const updated = familyMembers.filter((member) => member.id !== id);
    setFamilyMembers(updated);
    onUpdate(updated);
  };

  const updateFamilyMember = (
    id: string,
    field: keyof FamilyMember,
    value: string | boolean | number
  ) => {
    const updated = familyMembers.map((member) => {
      if (member.id === id) {
        const updatedMember = { ...member, [field]: value };
        // If hasCancer is set to false, clear cancer details
        if (field === "hasCancer" && value === false) {
          updatedMember.cancerType = undefined;
          updatedMember.ageAtDiagnosis = undefined;
        }
        return updatedMember;
      }
      return member;
    });
    setFamilyMembers(updated);
    onUpdate(updated);
  };

  return (
    <Card className="border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-[#3c4f3d] dark:text-white">
          <Users className="h-5 w-5" />
          Family History
        </CardTitle>
        <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
          Add family members and their cancer history. This helps assess your
          genetic risk.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {familyMembers.length === 0 ? (
          <div className="rounded-lg border border-dashed border-[#3c4f3d]/20 bg-[#e9eeea]/50 p-8 text-center dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a]/50">
            <Users className="mx-auto mb-3 h-12 w-12 text-[#3c4f3d]/30 dark:text-white/30" />
            <p className="mb-2 text-sm font-medium text-[#3c4f3d] dark:text-white">
              No family members added yet
            </p>
            <p className="mb-4 text-xs text-[#3c4f3d]/60 dark:text-white/60">
              Click the button below to start building your family history
            </p>
            <Button
              onClick={addFamilyMember}
              className="bg-[#de8246] hover:bg-[#de8246]/90"
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Family Member
            </Button>
          </div>
        ) : (
          <>
            <div className="space-y-3">
              {familyMembers.map((member, index) => (
                <div
                  key={member.id}
                  className="rounded-lg border border-[#3c4f3d]/10 bg-white p-4 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <span className="text-sm font-medium text-[#3c4f3d] dark:text-white">
                      Family Member {index + 1}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFamilyMember(member.id)}
                      className="h-8 w-8 p-0 text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950/30"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="space-y-3">
                    {/* Relationship */}
                    <div>
                      <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                        Relationship
                      </label>
                      <Select
                        value={member.relationship}
                        onValueChange={(value) =>
                          updateFamilyMember(member.id, "relationship", value)
                        }
                      >
                        <SelectTrigger className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#242924] dark:text-white/70">
                          <SelectValue placeholder="Select relationship" />
                        </SelectTrigger>
                        <SelectContent>
                          {RELATIONSHIPS.map((rel) => (
                            <SelectItem key={rel.value} value={rel.value}>
                              {rel.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Has Cancer */}
                    <div>
                      <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                        Cancer History
                      </label>
                      <Select
                        value={member.hasCancer ? "yes" : "no"}
                        onValueChange={(value) =>
                          updateFamilyMember(
                            member.id,
                            "hasCancer",
                            value === "yes"
                          )
                        }
                      >
                        <SelectTrigger className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#242924] dark:text-white/70">
                          <SelectValue placeholder="Select cancer history" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="no">No cancer history</SelectItem>
                          <SelectItem value="yes">Has/had cancer</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Cancer Details (only if hasCancer is true) */}
                    {member.hasCancer && (
                      <>
                        <div>
                          <label className="mb-1.5 block text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                            Type of Cancer
                          </label>
                          <Select
                            value={member.cancerType || ""}
                            onValueChange={(value) =>
                              updateFamilyMember(
                                member.id,
                                "cancerType",
                                value
                              )
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
                            value={member.ageAtDiagnosis || ""}
                            onChange={(e) =>
                              updateFamilyMember(
                                member.id,
                                "ageAtDiagnosis",
                                e.target.value ? parseInt(e.target.value) : 0
                              )
                            }
                            className="h-10 border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#242924] dark:text-white/70"
                          />
                        </div>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <Button
              onClick={addFamilyMember}
              variant="outline"
              className="w-full border-[#3c4f3d]/20 hover:border-[#de8246] hover:bg-[#de8246]/5 hover:text-[#de8246] dark:border-[#3c4f3d]/30"
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Another Family Member
            </Button>
          </>
        )}

        {familyMembers.length > 0 && (
          <div className="rounded-lg bg-blue-50 p-3 dark:bg-blue-950/20">
            <p className="text-xs text-blue-900 dark:text-blue-200">
              <strong>Tip:</strong> Include all blood relatives with cancer
              history, especially first-degree relatives (parents, siblings,
              children). Early age at diagnosis (before 50) is particularly
              important.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
