import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:fullscreen_window/fullscreen_window.dart';
import 'theme.dart';
import 'screens/merged_main_language_page.dart';
import 'screens/instructions_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Enable fullscreen mode
  await FullScreenWindow.setFullScreen(true);

  SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);

  runApp(const DementiaDetectorApp());
}

class DementiaDetectorApp extends StatefulWidget {
  const DementiaDetectorApp({super.key});

  @override
  _DementiaDetectorAppState createState() => _DementiaDetectorAppState();
}

class _DementiaDetectorAppState extends State<DementiaDetectorApp> {
  Locale? _locale;

  void setLocale(Locale locale) {
    setState(() {
      _locale = locale;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Dementia Detector',
      locale: _locale,
      supportedLocales: const [
        Locale('af'), // Afrikaans
        Locale('ar'), // Arabic
        Locale('bg'), // Bulgarian
        Locale('bn'), // Bengali
        Locale('ca'), // Catalan
        Locale('cs'), // Czech
        Locale('da'), // Danish
        Locale('de'), // German
        Locale('el'), // Greek
        Locale('en'), // English
        Locale('es'), // Spanish
        Locale('et'), // Estonian
        Locale('fa'), // Persian
        Locale('fi'), // Finnish
        Locale('fr'), // French
        Locale('gu'), // Gujarati
        Locale('he'), // Hebrew
        Locale('hi'), // Hindi
        Locale('hr'), // Croatian
        Locale('hu'), // Hungarian
        Locale('id'), // Indonesian
        Locale('it'), // Italian
        Locale('ja'), // Japanese
        Locale('kn'), // Kannada
        Locale('ko'), // Korean
        Locale('lt'), // Lithuanian
        Locale('lv'), // Latvian
        Locale('ml'), // Malayalam
        Locale('mr'), // Marathi
        Locale('nb'), // Norwegian Bokmål
        Locale('nl'), // Dutch
        Locale('pl'), // Polish
        Locale('pt'), // Portuguese
        Locale('ro'), // Romanian
        Locale('ru'), // Russian
        Locale('si'), // Sinhala
        Locale('sk'), // Slovak
        Locale('sl'), // Slovenian
        Locale('sq'), // Albanian
        Locale('sv'), // Swedish
        Locale('ta'), // Tamil
        Locale('te'), // Telugu
        Locale('th'), // Thai
        Locale('tl'), // Tagalog
        Locale('tr'), // Turkish
        Locale('uk'), // Ukrainian
        Locale('ur'), // Urdu
        Locale('vi'), // Vietnamese
        Locale('zh'), // Chinese
      ],
      localizationsDelegates: const [
        AppLocalizations.delegate, 
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      theme: ThemeData(
        fontFamily: 'Lexend',
        scaffoldBackgroundColor: AppColors.background,
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(50),
            ),
            padding: const EdgeInsets.symmetric(vertical: 14),
          ),
        ),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => MergedMainLanguagePage(onLocaleChange: setLocale),
        '/instructionsPage': (context) => const InstructionsPage(),
      },
    );
  }
}
