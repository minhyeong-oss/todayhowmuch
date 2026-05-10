package com.receipt.expensetracker.service;

import com.receipt.expensetracker.dto.OcrReceiptDto;
import com.receipt.expensetracker.entity.Category;
import com.receipt.expensetracker.entity.Expense;
import com.receipt.expensetracker.repository.CategoryRepository;
import com.receipt.expensetracker.repository.ExpenseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

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
        String categoryName = callLlm(dto.getStoreName());

        Category category = categoryRepository.findByCategoryName(categoryName)
                .orElseGet(() -> categoryRepository.save(
                        Category.builder().categoryName(categoryName).build()
                ));

        Expense expense = Expense.builder()
                .storeName(dto.getStoreName())
                .amountKrw(dto.getPrice())
                .spentOn(LocalDateTime.now())
                .category(category)
                .build();

        return expenseRepository.save(expense);
    }

    private String callLlm(String storeName) {
        try {
            RestTemplate restTemplate = new RestTemplate();
            String llmUrl = "http://10.0.10.6:11434/api/generate";

            Map<String, Object> request = new HashMap<>();
            request.put("model", "gemma3:1b");
            request.put("prompt",
                    "다음 상호명의 소비 카테고리를 식비, 카페, 교통, 쇼핑, 기타 중 하나만 답해라. " +
                            "다른 말은 하지 말고 카테고리명만 출력해라. 상호명: " + storeName);
            request.put("stream", false);

            Map response = restTemplate.postForObject(llmUrl, request, Map.class);
            if (response == null || response.get("response") == null) {
                return "기타";
            }

            String result = ((String) response.get("response")).trim();

            if (result.contains("식비")) return "식비";
            if (result.contains("카페")) return "카페";
            if (result.contains("교통")) return "교통";
            if (result.contains("쇼핑")) return "쇼핑";
            return "기타";

        } catch (Exception e) {
            return "기타";
        }
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
