package com.receipt.expensetracker.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity @Table(name = "llm_category_predictions")
@Getter @Builder @AllArgsConstructor @NoArgsConstructor(access = AccessLevel.PROTECTED)
public class LlmCategoryPrediction {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long predictionId;
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "expense_id")
    private Expense expense;
    private String predictedCategory;
    private Double confidenceScore;
}