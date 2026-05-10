package com.receipt.expensetracker.repository;

import com.receipt.expensetracker.entity.SpendingAnalysis;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SpendingAnalysisRepository extends JpaRepository<SpendingAnalysis, Long> {
}