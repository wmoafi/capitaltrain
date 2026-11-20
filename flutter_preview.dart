import 'package:flutter/material.dart';

void main() {
  runApp(const CapitalTrainApp());
}

class CapitalTrainApp extends StatelessWidget {
  const CapitalTrainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'قطار العاصمة LRT',
      debugShowCheckedModeBanner: false,
      locale: const Locale('ar'),
      theme: ThemeData(
        primarySwatch: Colors.sky,
        fontFamily: 'Cairo',
        useMaterial3: true,
      ),
      home: const Directionality(
        textDirection: TextDirection.rtl,
        child: HomeScreen(),
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final List<String> stations = [
    'عدلي منصور', 'العبور', 'المستقبل', 'الشروق', 'نيو هليوبوليس',
    'بدر', 'الروبيكي', 'حدائق العاصمة', 'مطار العاصمة', 'مدينة الفنون والثقافة',
    'المنطقة الصناعية', 'مدينة المعرفة'
  ];

  String fromStation = 'عدلي منصور';
  String toStation = 'مدينة الفنون والثقافة';

  int calculateTicket(int count) {
    if (count <= 3) return 10;
    if (count <= 7) return 15;
    return 20;
  }

  @override
  Widget build(BuildContext context) {
    int idx1 = stations.indexOf(fromStation);
    int idx2 = stations.indexOf(toStation);
    int count = (idx1 - idx2).abs();
    int price = calculateTicket(count);
    int estMinutes = count * 6;

    return Scaffold(
      appBar: AppBar(
        title: const Text('قطار العاصمة الكهربائي (LRT)', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.lightBlue[700],
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Next Train Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            color: Colors.lightBlue[800],
            child: const Padding(
              padding: EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Text('القطار القادم', style: TextStyle(color: Colors.white70, fontSize: 14)),
                  SizedBox(height: 8),
                  Text('10:00 ص', style: TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
                  SizedBox(height: 4),
                  Text('يصل خلال 10 دقائق (تقاطر منتظم)', style: TextStyle(color: Colors.amberAccent, fontSize: 13)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Trip Calculator
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('مخطط الرحلة وسعر التذكرة', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: fromStation,
                    decoration: const InputDecoration(labelText: 'محطة القيام', border: OutlineInputBorder()),
                    items: stations.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                    onChanged: (val) => setState(() => fromStation = val!),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: toStation,
                    decoration: const InputDecoration(labelText: 'محطة الوصول', border: OutlineInputBorder()),
                    items: stations.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                    onChanged: (val) => setState(() => toStation = val!),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue[50],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        Column(
                          children: [
                            const Text('سعر التذكرة', style: TextStyle(fontSize: 12, color: Colors.black54)),
                            Text('$price ج.م', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.blue)),
                          ],
                        ),
                        Column(
                          children: [
                            const Text('عدد المحطات', style: TextStyle(fontSize: 12, color: Colors.black54)),
                            Text('$count', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                          ],
                        ),
                        Column(
                          children: [
                            const Text('الوقت التقديري', style: TextStyle(fontSize: 12, color: Colors.black54)),
                            Text('$estMinutes دقيقة', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ],
                    ),
                  )
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
