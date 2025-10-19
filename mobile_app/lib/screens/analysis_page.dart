import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../theme.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'result_page.dart';

class AnalysisPage extends StatefulWidget {
  const AnalysisPage({super.key});

  @override
  State<AnalysisPage> createState() => _AnalysisPageState();
}

class _AnalysisPageState extends State<AnalysisPage> {
  late Timer _timer;
  int _remainingSeconds = 60 * 6;
  bool _uploading = false;
  bool _analysisComplete = false;
  String? _analysisResult;

  @override
  void initState() {
    super.initState();
    _startTimer();
    _fetchAnalysisResult();
  }

  @override
  void dispose() {
    if (_timer.isActive) {
      _timer.cancel();
    }
    super.dispose();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_remainingSeconds > 0) {
        setState(() {
          _remainingSeconds--;
        });
      }
    });
  }

  Future<bool> _isUploadComplete() async {
    try {
      final response = await http.get(
        Uri.parse('https://sculpin-curious-antelope.ngrok-free.app/upload-status'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['complete'];
      }
    } catch (e) {
      print('Error checking upload status: $e');
    }
    return false;
  }


  Future<void> _fetchAnalysisResult() async {
    if (_uploading) return;
    setState(() {
      _uploading = true;
    });

    try {
      bool uploadComplete = false;
      while (!uploadComplete) {
        uploadComplete = await _isUploadComplete();
        if (!uploadComplete) {
          await Future.delayed(const Duration(seconds: 2)); // Retry every 2 seconds
        }
      }

      final response = await http.get(
        Uri.parse('https://sculpin-curious-antelope.ngrok-free.app/get_classification'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        String classification = data['classification'];

        if (mounted) {
          setState(() {
            _analysisComplete = true;
            _analysisResult = classification;
          });
        }
        _timer.cancel(); // Stop timer
      } else {
        print('Failed to fetch analysis result');
      }
    } catch (e) {
      print('Error: $e');
    } finally {
      if (mounted) {
        setState(() {
          _uploading = false;
        });
      }
    }
  }

  Future<void> _cancelAnalysis() async {
    try {
      var response = await http.post(Uri.parse('https://sculpin-curious-antelope.ngrok-free.app/cancel'));
      if (response.statusCode == 200) {
        print('Analysis cancelled successfully on server');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  void _navigateToResultPage(String result) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ResultPage(result: result),
      ),
    );
  }

  String _formatTime(int seconds) {
    final minutes = (seconds ~/ 60).toString().padLeft(2, '0');
    final secs = (seconds % 60).toString().padLeft(2, '0');
    return "$minutes:$secs";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(context),
            const SizedBox(height: 16),
            _buildStatusText(context),
            const SizedBox(height: 24),
            _buildTimerDisplay(),
            const Spacer(),
            _buildResultButton(context),
            _buildCancelButton(context),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back, color: AppColors.secondary),
            onPressed: () => Navigator.pop(context),
          ),
          const Spacer(),
          Text(
            AppLocalizations.of(context)!.aiAnalysis,
            style: AppTextStyles.heading,
          ),
          const Spacer(flex: 2),
        ],
      ),
    );
  }

  Widget _buildStatusText(BuildContext context) {
    return Text(
      _analysisComplete
          ? AppLocalizations.of(context)!.analyzationFinished
          : AppLocalizations.of(context)!.analyzingDescription,
      textAlign: TextAlign.center,
      style: AppTextStyles.body,
    );
  }

  Widget _buildTimerDisplay() {
    if (_analysisComplete) {
      return Center(
        child: Text(
          AppLocalizations.of(context)!.resultReady,
          style: AppTextStyles.heading.copyWith(fontSize: 32),
        ),
      );
    }
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        height: 80,
        decoration: BoxDecoration(
          color: AppColors.border,
          borderRadius: AppBorders.borderRadius,
        ),
        alignment: Alignment.center,
        child: Text(
          _formatTime(_remainingSeconds),
          style: AppTextStyles.heading.copyWith(fontSize: 32),
        ),
      ),
    );
  }

  Widget _buildResultButton(BuildContext context) {
    if (_analysisComplete) {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        child: ElevatedButton(
          onPressed: () {
            _navigateToResultPage(_analysisResult!);
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            shape: RoundedRectangleBorder(
              borderRadius: AppBorders.borderRadius,
            ),
            padding: const EdgeInsets.symmetric(vertical: 14),
            minimumSize: const Size(double.infinity, 50),
          ),
          child: Text(
            AppLocalizations.of(context)!.viewResults,
            style: AppTextStyles.button.copyWith(color: AppColors.white),
          ),
        ),
      );
    }
    return Container();
  }

  Widget _buildCancelButton(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ElevatedButton(
        onPressed: () async {
          await _cancelAnalysis();
          Navigator.pop(context);
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.border,
          shape: RoundedRectangleBorder(
            borderRadius: AppBorders.borderRadius,
          ),
          padding: const EdgeInsets.symmetric(vertical: 14),
          minimumSize: const Size(double.infinity, 50),
        ),
        child: Text(
          AppLocalizations.of(context)!.cancelAnalysis,
          style: AppTextStyles.button.copyWith(color: AppColors.secondary),
        ),
      ),
    );
  }
}
