package com.receipt.expensetracker.repository;

import com.receipt.expensetracker.entity.OcrResult;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OcrResultRepository extends JpaRepository<OcrResult, Long> {
}