package com.receipt.expensetracker.service;

import com.receipt.expensetracker.dto.OcrReceiptDto;
import com.receipt.expensetracker.entity.Category;
import com.receipt.expensetracker.entity.Expense;
import com.receipt.expensetracker.repository.CategoryRepository;
import com.receipt.expensetracker.repository.ExpenseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ExpenseService {

    private final ExpenseRepository expenseRepository;
    private final CategoryRepository categoryRepository;

    public List<Expense> getAllExpenses() {
        return expenseRepository.findAll();
    }

    public Expense saveFromOcr(OcrReceiptDto dto) {
        Category category = categoryRepository.findByCategoryName("기타")
                .orElseGet(() -> categoryRepository.save(
                        Category.builder().categoryName("기타").build()
                ));

        Expense expense = Expense.builder()
                .storeName(dto.getStoreName())
                .amountKrw(dto.getPrice())
                .spentOn(LocalDateTime.now())
                .category(category)
                .build();

        return expenseRepository.save(expense);
    }

    public Map<String, Object> getSummary() {
        List<Expense> expenses = expenseRepository.findAll();
        Map<String, Double> categoryTotals = expenses.stream()
                .filter(e -> e.getCategory() != null)
                .collect(Collectors.groupingBy(
                        e -> e.getCategory().getCategoryName(),
                        Collectors.summingDouble(e -> e.getAmountKrw() != null ? e.getAmountKrw() : 0)
                ));
        double totalAmount = expenses.stream()
                .mapToDouble(e -> e.getAmountKrw() != null ? e.getAmountKrw() : 0)
                .sum();
        String topCategory = categoryTotals.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("없음");
        Map<String, Object> result = new HashMap<>();
        result.put("totalAmount", totalAmount);
        result.put("totalCount", expenses.size());
        result.put("categoryTotals", categoryTotals);
        result.put("topCategory", topCategory);
        return result;
    }

    public List<Map<String, Object>> getMonthlyTrend() {
        List<Expense> expenses = expenseRepository.findAll();
        Map<String, Double> monthlyMap = expenses.stream()
                .filter(e -> e.getSpentOn() != null)
                .collect(Collectors.groupingBy(
                        e -> e.getSpentOn().getYear() + "-" +
                                String.format("%02d", e.getSpentOn().getMonthValue()),
                        Collectors.summingDouble(e -> e.getAmountKrw() != null ? e.getAmountKrw() : 0)
                ));
        return monthlyMap.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .map(entry -> {
                    Map<String, Object> m = new HashMap<>();
                    m.put("월", entry.getKey());
                    m.put("총 지출액", entry.getValue());
                    return m;
                })
                .collect(Collectors.toList());
    }
}