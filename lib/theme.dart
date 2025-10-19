import 'package:flutter/material.dart';

// Define your color palette
class AppColors {
  static const background = Color(0xFFF8FAFC);
  static const primary = Color(0xFF451e58);
  static const secondary = Color(0xFF0E141B);
  static const accent = Color(0xFF4E7397);
  static const border = Color(0xFFF8FAFC);
  static const white = Colors.white;
  static const text = Colors.black;
}

// Define your text styles
class AppTextStyles {
  static const TextStyle heading = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: AppColors.secondary,
    fontFamily: 'Lexend',
  );

  static const TextStyle body = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: AppColors.secondary,
    fontFamily: 'Lexend',
  );

  static const TextStyle bodyBold = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.bold,
    color: AppColors.secondary,
    fontFamily: 'Lexend',
  );

  static const TextStyle hint = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w500,
    color: AppColors.accent,
    fontFamily: 'Lexend',
  );

  static const TextStyle button = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.bold,
    color: AppColors.white,
    fontFamily: 'Lexend',
  );
}

// Define your border styles
class AppBorders {
  static const BorderRadius borderRadius = BorderRadius.all(Radius.circular(50));
  static const OutlineInputBorder inputBorder = OutlineInputBorder(
    borderRadius: borderRadius,
    borderSide: BorderSide(color: AppColors.border),
  );
}
