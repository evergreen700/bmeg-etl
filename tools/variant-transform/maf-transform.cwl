
cwlVersion: v1.0
class: CommandLineTool
hints:
  DockerRequirement:
    dockerPull: biostream/variant-transform:latest

baseCommand:
  - python
  - /opt/ga4gh-variant.py

arguments:
  - "--multi"
  - maf_data

inputs:
  MAF:
    type: File
    inputBinding:
      prefix: "--maf"
  
  BIOPREFIX:
    type: string
    inputBinding: 
      prefix: "--bioPrefix"
  
  CALLSETPREFIX:
    type: string
    inputBinding:
      prefix: "--callSetPrefix"
  
  GENECOL:
    type: string?
    inputBinding:
      prefix: "--gene"

outputs:
  VARIANT:
    type: File
    outputBinding:
      glob: "maf_data.ga4gh.Variant.json"
  VARIANT_ANNOTATION:
    type: File
    outputBinding:
      glob: "maf_data.ga4gh.VariantAnnotation.json"
  CALLSET:
    type: File
    outputBinding:
       glob: "maf_data.ga4gh.CallSet.json"
