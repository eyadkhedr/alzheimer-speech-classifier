import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:universal_dementia_detector/theme.dart';

class ResultPage extends StatelessWidget {
  final String result;

  const ResultPage({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    String title;
    String message;
    String recommendation;
    Color messageColor;

    if (result == 'AD') {
      title = AppLocalizations.of(context)!.dementia_title;
      message = AppLocalizations.of(context)!.dementia_message;
      recommendation = AppLocalizations.of(context)!.dementia_recommendation;
      messageColor = Colors.red;  // Color for dementia message
    } else if (result == 'HC') {
      title = AppLocalizations.of(context)!.healthy_title;
      message = AppLocalizations.of(context)!.healthy_message;
      recommendation = AppLocalizations.of(context)!.healthy_recommendation;
      messageColor = Colors.green;  // Color for healthy message
    } else {
      title = AppLocalizations.of(context)!.result;
      message = 'Unknown classification';
      recommendation = '';
      messageColor = Colors.black;  // Default color for unknown classification
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(title),
        backgroundColor: AppColors.background,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                message,
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: messageColor),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 16),
              Text(
                recommendation,
                style: TextStyle(fontSize: 16),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
