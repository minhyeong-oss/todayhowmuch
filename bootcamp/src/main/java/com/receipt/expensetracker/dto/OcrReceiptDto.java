package com.receipt.expensetracker.dto;

import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class OcrReceiptDto {
    private String storeName;
    private Double price;
}