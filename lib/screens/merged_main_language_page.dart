import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import '../theme.dart';

class MergedMainLanguagePage extends StatefulWidget {
  final Function(Locale) onLocaleChange;

  const MergedMainLanguagePage({super.key, required this.onLocaleChange});

  @override
  State<MergedMainLanguagePage> createState() => _MergedMainLanguagePageState();
}

class _MergedMainLanguagePageState extends State<MergedMainLanguagePage> {
  Locale? selectedLanguage;
  String? displayedLanguage;
  bool isLoading = false;
  String? errorMessage;

  final Map<String, String> languageNames = {
    'zh': '中文',
    'en': 'English',
    'ar': 'العربية',
    'hi': 'हिंदी',
    'es': 'Español',
    'bn': 'বাংলা',
    'pt': 'Português',
    'fr': 'Français',
    'ru': 'Русский',
    'ur': 'اردو',
    'ja': '日本語',
    'de': 'Deutsch',
    'vi': 'Tiếng Việt',
    'te': 'తెలుగు',
    'mr': 'मराठी',
    'kn': 'ಕನ್ನಡ',
    'id': 'Bahasa Indonesia',
    'ml': 'മലയാളം',
    'ta': 'தமிழ்',
    'tr': 'Türkçe',
    'th': 'ไทย',
    'it': 'Italiano',
    'pl': 'Polski',
    'nl': 'Nederlands',
    'he': 'עברית',
    'ca': 'Català',
    'bg': 'Български',
    'sq': 'Shqip',
    'af': 'Afrikaans',
    'sk': 'Slovenčina',
    'nb': 'Norsk Bokmål',
    'fi': 'Suomi',
    'da': 'Dansk',
    'el': 'Ελληνικά',
    'hu': 'Magyar',
    'si': 'සිංහල',
    'gu': 'ગુજરાતી',
    'et': 'Eesti',
    'lt': 'Lietuvių',
    'lv': 'Latviešu',
    'sl': 'Slovenščina',
    'cs': 'Čeština',
    'sv': 'Svenska',
    'uk': 'Українська',
    'tl': 'Tagalog',
    'fa': 'فارسی',
    'ko': '한국어',
    'hr': 'Hrvatski',
    'ro': 'Română',
  };


  Future<void> sendLanguageCodeToServer(String languageCode) async {
    const String url = "https://sculpin-curious-antelope.ngrok-free.app/selected-language";
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'languageCode': languageCode}),
      );

      if (response.statusCode == 200) {
        setState(() {
          isLoading = false;
          displayedLanguage = languageNames[languageCode] ?? AppLocalizations.of(context)!.unknownLanguage;
        });
      } else {
        setState(() {
          isLoading = false;
          errorMessage = AppLocalizations.of(context)!.serverError;
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = AppLocalizations.of(context)!.connectionError;
      });
    }
  }

  void handleContinue() async {
    if (selectedLanguage == null) {
      setState(() {
        errorMessage = AppLocalizations.of(context)!.selectLanguageError;
      });
      return;
    }

    await sendLanguageCodeToServer(selectedLanguage!.languageCode);

    if (errorMessage == null) {
      Navigator.pushNamed(context, '/instructionsPage');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Spacer(),
            const Center(
              child: Icon(
                Icons.language,
                size: 100,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              AppLocalizations.of(context)!.appTitle,
              textAlign: TextAlign.center,
              style: AppTextStyles.heading,
            ),
            const SizedBox(height: 16),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    AppLocalizations.of(context)!.chooseLanguage,
                    style: AppTextStyles.bodyBold,
                  ),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<Locale>(
                    value: selectedLanguage,
                    items: languageNames.entries
                        .map((entry) => DropdownMenuItem(
                              value: Locale(entry.key),
                              child: Text(entry.value),
                            ))
                        .toList(),
                    onChanged: (locale) {
                      setState(() {
                        selectedLanguage = locale;
                        displayedLanguage = locale != null
                            ? languageNames[locale.languageCode]
                            : null;
                        errorMessage = null; // Clear error if any
                      });
                      if (locale != null) {
                        widget.onLocaleChange(locale);
                      }
                    },
                    decoration: InputDecoration(
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 15,
                        vertical: 14,
                      ),
                      border: AppBorders.inputBorder,
                      filled: true,
                      fillColor: AppColors.background,
                    ),
                    hint: Text(
                      AppLocalizations.of(context)!.selectLanguage,
                      style: AppTextStyles.hint,
                    ),
                    dropdownColor: AppColors.background,
                    style: AppTextStyles.body,
                  ),
                  if (displayedLanguage != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      AppLocalizations.of(context)!
                          .selectedLanguageMessage(displayedLanguage!),
                      style: AppTextStyles.body,
                    ),
                  ],
                  if (errorMessage != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      errorMessage!,
                      style: AppTextStyles.body.copyWith(color: Colors.red),
                    ),
                  ],
                ],
              ),
            ),
            const Spacer(),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: ElevatedButton(
                onPressed: isLoading ? null : handleContinue,
                child: isLoading
                    ? const CircularProgressIndicator(
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      )
                    : Text(
                        AppLocalizations.of(context)!.continue_button,
                        style: AppTextStyles.button,
                      ),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
