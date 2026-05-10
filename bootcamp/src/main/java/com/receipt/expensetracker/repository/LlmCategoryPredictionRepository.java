package com.receipt.expensetracker.repository;

import com.receipt.expensetracker.entity.LlmCategoryPrediction;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LlmCategoryPredictionRepository extends JpaRepository<LlmCategoryPrediction, Long> {
}