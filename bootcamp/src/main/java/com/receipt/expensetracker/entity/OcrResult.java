package com.receipt.expensetracker.entity;

import jakarta.persistence.*;
import lombok.*;


@Entity @Table(name = "ocr_results")
@Getter @Builder @AllArgsConstructor @NoArgsConstructor(access = AccessLevel.PROTECTED)
public class OcrResult {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long ocrId;
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "receipt_id")
    private Receipt receipt;
    @Column(columnDefinition = "TEXT")
    private String rawText; // OCR이 추출한 전체 텍스트
}