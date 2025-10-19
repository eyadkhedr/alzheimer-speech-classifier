import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import '../theme.dart';
import 'recording_page.dart';

class InstructionsPage extends StatelessWidget {
  const InstructionsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        leading: BackButton(
          color: AppColors.text, // Set the color of the back button
          onPressed: () {
            Navigator.pop(context); // Navigate back to the previous page
          },
        ),
      ),
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                AppLocalizations.of(context)!.instructions,
                textAlign: TextAlign.center,
                style: AppTextStyles.heading,
              ),
            ),
            const SizedBox(height: 16),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: RichText(
                text: TextSpan(
                  style: AppTextStyles.bodyBold.copyWith(color: AppColors.text),
                  children: [
                    _parseInstruction(AppLocalizations.of(context)!.instruction1),
                    const TextSpan(text: "\n\n"),
                    _parseInstruction(AppLocalizations.of(context)!.instruction2),
                    const TextSpan(text: "\n\n"),
                    _parseInstruction(AppLocalizations.of(context)!.instruction3),
                  ],
                ),
              ),
            ),
            const Spacer(),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const RecordingPage(),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  minimumSize: const Size(double.infinity, 50),
                  shape: RoundedRectangleBorder(
                    borderRadius: AppBorders.borderRadius,
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
                child: Text(
                  AppLocalizations.of(context)!.startRecording,
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

  TextSpan _parseInstruction(String instruction) {
    // Split instruction into parts based on Markdown-style bold "**"
    final regex = RegExp(r'\*\*(.*?)\*\*');
    final spans = <TextSpan>[];
    int start = 0;

    for (final match in regex.allMatches(instruction)) {
      if (match.start > start) {
        spans.add(TextSpan(
          text: instruction.substring(start, match.start),
          style: AppTextStyles.body,
        ));
      }
      spans.add(TextSpan(
        text: match.group(1),
        style: AppTextStyles.bodyBold,
      ));
      start = match.end;
    }

    if (start < instruction.length) {
      spans.add(TextSpan(
        text: instruction.substring(start),
        style: AppTextStyles.body,
      ));
    }

    return TextSpan(children: spans);
  }
}
