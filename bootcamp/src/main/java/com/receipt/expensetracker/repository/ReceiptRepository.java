package com.receipt.expensetracker.repository;

import com.receipt.expensetracker.entity.Receipt;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReceiptRepository extends JpaRepository<Receipt, Long> {
}