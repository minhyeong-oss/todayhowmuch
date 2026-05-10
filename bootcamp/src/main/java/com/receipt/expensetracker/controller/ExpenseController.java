package com.receipt.expensetracker.controller;

import com.receipt.expensetracker.dto.OcrReceiptDto;
import com.receipt.expensetracker.entity.Expense;
import com.receipt.expensetracker.service.ExpenseService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/expenses")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ExpenseController {

    private final ExpenseService expenseService;

    @GetMapping
    public List<Expense> getExpenseList() {
        return expenseService.getAllExpenses();
    }

    @GetMapping("/summary")
    public Map<String, Object> getSummary() {
        return expenseService.getSummary();
    }

    @GetMapping("/monthly")
    public List<Map<String, Object>> getMonthlyTrend() {
        return expenseService.getMonthlyTrend();
    }

    @PostMapping("/upload")
    public Expense uploadFromOcr(@RequestBody OcrReceiptDto dto) {
        return expenseService.saveFromOcr(dto);
    }
}