import 'dart:async';
import 'dart:io'; // <-- For file deletion
import 'package:flutter/material.dart';
import 'package:audio_waveforms/audio_waveforms.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart'; // <-- Add this import
import '../theme.dart';
import 'analysis_page.dart';

class RecordingPage extends StatefulWidget {
  const RecordingPage({super.key});

  @override
  State<RecordingPage> createState() => _RecordingPageState();
}

class _RecordingPageState extends State<RecordingPage> {
  final RecorderController _recorderController = RecorderController();
  final PlayerController _playerController = PlayerController();
  String serverUrl = "https://sculpin-curious-antelope.ngrok-free.app";
  bool isRecording = false;
  bool isPlaying = false;
  bool hasRecording = false;
  bool isPlayerPrepared = false;
  String? filePath;
  String recordingTime = "00:00";
  Timer? _timer;
  int _millisecondsElapsed = 0;

  @override
  void initState() {
    super.initState();
    _initializeRecorder();

    // Update frequency for smoother timeline
    _playerController.updateFrequency = UpdateFrequency.high;

    // Handle playback completion
    _playerController.onCompletion.listen((_) async {
      await _playerController.stopPlayer();
      setState(() {
        isPlaying = false; // Reset the playback button state
        isPlayerPrepared = false;
      });
      if (!isPlayerPrepared && filePath != null) {
        await _playerController.preparePlayer(path: filePath!);
        isPlayerPrepared = true;
      }
      await _playerController.startPlayer();
      await _playerController.pausePlayer();
      print("debug message: player completed audio");
    });
  }

  @override
  void dispose() {
    _recorderController.dispose();
    _playerController.dispose();
    _timer?.cancel();
    super.dispose();
  }

  void _initializeRecorder() {
    _recorderController
      ..androidEncoder = AndroidEncoder.aac
      ..androidOutputFormat = AndroidOutputFormat.mpeg4
      ..iosEncoder = IosEncoder.kAudioFormatMPEG4AAC
      ..sampleRate = 16000
      ..bitRate = 160000;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(context),
            const SizedBox(height: 16),
            _buildImageDisplay(),
            const SizedBox(height: 16),
            _buildAudioWave(),
            const SizedBox(height: 16),
            _buildTimerDisplay(),
            const SizedBox(height: 32),
            _buildActionButtons(context),
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
            AppLocalizations.of(context)!.recording,
            style: AppTextStyles.heading,
          ),
          const Spacer(flex: 2),
        ],
      ),
    );
  }

  Widget _buildImageDisplay() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: AppColors.primary, width: 3),
          borderRadius: BorderRadius.circular(16),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Image.asset(
            "assets/images/cookie_test.png",
            height: 250,
            width: double.infinity,
            fit: BoxFit.cover,
          ),
        ),
      ),
    );
  }

  Widget _buildAudioWave() {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 300),
      transitionBuilder: (Widget child, Animation<double> animation) {
        return FadeTransition(
          opacity: animation,
          child: SizeTransition(
            sizeFactor: animation,
            axis: Axis.horizontal,
            child: child,
          ),
        );
      },
      child: hasRecording
          ? Padding(
              key: const ValueKey('playbackWaveformContainer'),
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: ShaderMask(
                shaderCallback: (Rect bounds) {
                  return LinearGradient(
                    colors: [
                      Colors.transparent,
                      AppColors.primary,
                      Colors.transparent,
                    ],
                    stops: const [0.0, 0.5, 1.0],
                  ).createShader(bounds);
                },
                blendMode: BlendMode.dstIn,
                child: AudioFileWaveforms(
                  continuousWaveform: true,
                  key: const ValueKey('playbackWaveform'),
                  playerController: _playerController,
                  size: const Size(double.infinity, 50),
                  playerWaveStyle: const PlayerWaveStyle(
                    fixedWaveColor: AppColors.accent,
                    liveWaveColor: AppColors.primary,
                  ),
                ),
              ),
            )
          : Padding(
              key: const ValueKey('recordingWaveformContainer'),
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: ShaderMask(
                shaderCallback: (Rect bounds) {
                  return LinearGradient(
                    colors: [
                      Colors.transparent,
                      AppColors.primary,
                      Colors.transparent,
                    ],
                    stops: const [0.0, 0.5, 1.0],
                  ).createShader(bounds);
                },
                blendMode: BlendMode.dstIn,
                child: AudioWaveforms(
                  key: const ValueKey('recordingWaveform'),
                  enableGesture: !isRecording,
                  size: Size(MediaQuery.of(context).size.width - 32, 50),
                  recorderController: _recorderController,
                  waveStyle: const WaveStyle(
                    waveColor: AppColors.primary,
                    extendWaveform: true,
                    showMiddleLine: false,
                  ),
                ),
              ),
            ),
    );
  }

  Widget _buildTimerDisplay() {
    return Text(
      recordingTime,
      style: AppTextStyles.heading.copyWith(fontSize: 20),
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    return Column(
      children: [
        _buildPlaybackButton(),
        const SizedBox(height: 16),
        _buildRecordButton(),
        const SizedBox(height: 16),
        _buildUploadButton(), // <-- New Upload Audio button
        const SizedBox(height: 16),
        _buildAnalyzeButton(context),
      ],
    );
  }

  Widget _buildPlaybackButton() {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 200),
      transitionBuilder: (Widget child, Animation<double> animation) {
        return FadeTransition(
          opacity: animation,
          child: SizeTransition(
            sizeFactor: animation,
            child: child,
          ),
        );
      },
      child: hasRecording
          ? Center(
              key: ValueKey<bool>(hasRecording),
              child: GestureDetector(
                onTap: () async {
                  try {
                    if (isPlaying) {
                      await _playerController.pausePlayer();
                    } else {
                      if (!isPlayerPrepared) {
                        if (filePath != null) {
                          await _playerController.preparePlayer(path: filePath!);
                          setState(() => isPlayerPrepared = true);
                        } else {
                          return; // File path is null, do nothing
                        }
                      }
                      await _playerController.startPlayer();
                    }
                    setState(() => isPlaying = !isPlaying);
                  } catch (e) {
                    _showErrorMessage("Error during playback: ${e.toString()}");
                  }
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  width: 70,
                  height: 70,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isPlaying ? Colors.red : AppColors.primary,
                  ),
                  child: Icon(
                    isPlaying ? Icons.pause : Icons.play_arrow,
                    color: Colors.white,
                    size: 40,
                  ),
                ),
              ),
            )
          : SizedBox.shrink(key: ValueKey<bool>(hasRecording)),
    );
  }

  Widget _buildRecordButton() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ElevatedButton(
        onPressed: _toggleRecording,
        style: ElevatedButton.styleFrom(
          backgroundColor: isRecording ? Colors.red : AppColors.primary,
          shape: RoundedRectangleBorder(
            borderRadius: AppBorders.borderRadius,
          ),
          padding: const EdgeInsets.symmetric(vertical: 14),
          minimumSize: const Size(double.infinity, 50),
        ),
        child: Text(
          isRecording
              ? AppLocalizations.of(context)!.stopRecording
              : AppLocalizations.of(context)!.startRecording,
          style: AppTextStyles.button,
        ),
      ),
    );
  }

  // New "Upload Audio" button widget
  Widget _buildUploadButton() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ElevatedButton(
        onPressed: _pickAudioFile,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          shape: RoundedRectangleBorder(
            borderRadius: AppBorders.borderRadius,
          ),
          padding: const EdgeInsets.symmetric(vertical: 14),
          minimumSize: const Size(double.infinity, 50),
        ),
        child: Text(
          AppLocalizations.of(context)!.uploadAudio, // Ensure you add this key in your localization files
          style: AppTextStyles.button,
        ),
      ),
    );
  }

  Widget _buildAnalyzeButton(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ElevatedButton(
        onPressed: filePath != null && !isRecording ? () => _sendTestFileAndNavigate(context) : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: filePath != null ? AppColors.primary : AppColors.border,
          shape: RoundedRectangleBorder(
            borderRadius: AppBorders.borderRadius,
          ),
          padding: const EdgeInsets.symmetric(vertical: 14),
          minimumSize: const Size(double.infinity, 50),
        ),
        child: Text(
          AppLocalizations.of(context)!.analyzeRecording,
          style: AppTextStyles.button.copyWith(
            color: filePath != null ? AppColors.white : AppColors.accent,
          ),
        ),
      ),
    );
  }

  // Modified _toggleRecording: Delete previous recording (if any) before starting a new one.
  Future<void> _toggleRecording() async {
    try {
      if (isRecording) {
        String? path = await _recorderController.stop();
        _stopTimer();

        if (path != null) {
          filePath = path;
          await _playerController.preparePlayer(path: filePath!);
          isPlayerPrepared = true;
          setState(() {
            isRecording = false;
            hasRecording = true;
          });
        } else {
          setState(() {
            isRecording = false;
            hasRecording = false;
          });
        }
      } else {
        // Delete previous file if it exists before starting a new recording
        if (filePath != null) {
          final oldFile = File(filePath!);
          if (await oldFile.exists()) {
            await oldFile.delete();
          }
          filePath = null;
          setState(() {
            hasRecording = false;
            isPlayerPrepared = false;
          });
        }
        final dir = await getApplicationDocumentsDirectory();
        filePath = p.join(dir.path, "recording_${DateTime.now().millisecondsSinceEpoch}.wav");
        await _recorderController.record(path: filePath!);
        _startTimer();
        setState(() {
          isRecording = true;
          hasRecording = false;
        });
      }
    } catch (e) {
      _showErrorMessage("Recording error: ${e.toString()}");
    }
  }

  // New method to pick an audio file from device storage.
  Future<void> _pickAudioFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['wav', 'mp3', 'm4a'],
      );
      if (result != null && result.files.single.path != null) {
        // If a file was previously recorded/uploaded, delete it.
        if (filePath != null) {
          final oldFile = File(filePath!);
          if (await oldFile.exists()) {
            await oldFile.delete();
          }
        }
        String pickedPath = result.files.single.path!;
        setState(() {
          filePath = pickedPath;
          hasRecording = true;
          isPlayerPrepared = false;
        });
        await _playerController.preparePlayer(path: filePath!);
        setState(() {
          isPlayerPrepared = true;
        });
      }
    } catch (e) {
      _showErrorMessage("Error picking file: ${e.toString()}");
    }
  }

  Future<void> _sendFileToServer(String url, String filePath, String fileType) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse(url));
      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      final response = await request.send();
      if (response.statusCode == 200) {
        if (fileType == "test") {
          if (!mounted) return;
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AnalysisPage()),
          );
        }
      } else {
        _showErrorMessage(AppLocalizations.of(context)!.connectionFailed);
      }
    } catch (e) {
      _showErrorMessage(AppLocalizations.of(context)!.connectionError);
    }
  }

  Future<void> _sendTestFileAndNavigate(BuildContext context) async {
    final testFilePath = p.join((await getApplicationDocumentsDirectory()).path, "test_connection.wav");

    // Create and save a very small test file
    await _recorderController.record(path: testFilePath);
    await _recorderController.stop();

    // Upload the test file
    await _sendFileToServer("$serverUrl/test-connection", testFilePath, "test");

    // Upload the actual recording after the test file is successful
    if (filePath != null) {
      await _sendFileToServer("$serverUrl/upload", filePath!, "recording");
    }
  }

  void _startTimer() {
    _millisecondsElapsed = 0;
    _timer = Timer.periodic(
      const Duration(milliseconds: 10),
      (timer) {
        _millisecondsElapsed += 10;
        if (_millisecondsElapsed % 100 == 0) {
          setState(() {
            recordingTime = _formatDuration(_millisecondsElapsed);
          });
        }
      },
    );
  }

  void _stopTimer() {
    _timer?.cancel();
    _timer = null;
  }

  String _formatDuration(int milliseconds) {
    final minutes = (milliseconds ~/ 60000).toString().padLeft(2, '0');
    final seconds = ((milliseconds % 60000) ~/ 1000).toString().padLeft(2, '0');
    return "$minutes:$seconds";
  }

  void _showErrorMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }
}
