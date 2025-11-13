from typing import Literal, TypeAlias

__all__ = ["ExperimentResultFileFormat"]

ExperimentResultFileFormat: TypeAlias = Literal[
    "SAM", "BAM", "CRAM", "VCF", "BCF", "MAF", "GVCF", "BigWig", "BigBed", "FASTA", "FASTQ", "TAB",
    "SRA", "SRF", "SFF", "GFF", "PDF", "CSV", "TSV", "JPEG", "PNG", "GIF", "HTML", "MARKDOWN",
    "MP3", "M4A", "MP4", "DOCX", "XLS", "XLSX", "UNKNOWN", "OTHER",
]
