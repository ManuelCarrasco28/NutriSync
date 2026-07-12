import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';

class IndicacionesTab extends StatefulWidget {
  const IndicacionesTab({super.key});

  @override
  State<IndicacionesTab> createState() => _IndicacionesTabState();
}

class _IndicacionesTabState extends State<IndicacionesTab> with SingleTickerProviderStateMixin {
  late TabController _innerTabController;
  bool _loading = false;
  List<dynamic> _notas = [];
  List<dynamic> _recomendaciones = [];
  String? _errorMsg;

  @override
  void initState() {
    super.initState();
    _innerTabController = TabController(length: 2, vsync: this);
    _cargarDatos();
  }

  @override
  void dispose() {
    _innerTabController.dispose();
    super.dispose();
  }

  Future<void> _cargarDatos() async {
    setState(() {
      _loading = true;
      _errorMsg = null;
    });

    try {
      final notasData = await ApiService.getNotas();
      final recomData = await ApiService.getRecomendaciones();
      if (mounted) {
        setState(() {
          _notas = notasData;
          _recomendaciones = recomData;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMsg = 'No se pudieron cargar las indicaciones médicas. Verifica tu conexión.';
          _loading = false;
        });
      }
    }
  }

  Widget _buildNotasTab(bool isDark) {
    if (_notas.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.note_alt_outlined, size: 64, color: Colors.grey),
            const SizedBox(height: 12),
            Text(
              'No hay notas clínicas registradas aún.',
              style: TextStyle(color: isDark ? Colors.grey[400] : Colors.grey[600], fontSize: 14),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _notas.length,
      itemBuilder: (context, index) {
        final nota = _notas[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          color: isDark ? const Color(0xFF1C1D24) : Colors.white,
          elevation: 2,
          shadowColor: Colors.black.withValues(alpha: 0.05),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ExpansionTile(
            title: Text(
              nota['titulo'] ?? 'Nota de Consulta',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
            subtitle: Text(
              '${nota['tipo']} — ${nota['fecha']}',
              style: const TextStyle(fontSize: 12, color: Color(0xFF10B981)),
            ),
            childrenPadding: const EdgeInsets.all(16),
            expandedCrossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (nota['motivo_consulta'] != null && nota['motivo_consulta'].toString().isNotEmpty) ...[
                _buildSectionDetail('Motivo de Consulta', nota['motivo_consulta'] ?? ''),
                const Divider(height: 20),
              ],
              if (nota['resumen_consulta'] != null && nota['resumen_consulta'].toString().isNotEmpty) ...[
                _buildSectionDetail('Resumen de Consulta', nota['resumen_consulta'] ?? ''),
                const Divider(height: 20),
              ],
              if (nota['objetivos_acordados'] != null && nota['objetivos_acordados'].toString().isNotEmpty) ...[
                _buildSectionDetail('Objetivos Acordados', nota['objetivos_acordados'] ?? ''),
                const Divider(height: 20),
              ],
              if (nota['plan_accion'] != null && nota['plan_accion'].toString().isNotEmpty) ...[
                _buildSectionDetail('Plan de Acción', nota['plan_accion'] ?? ''),
                const Divider(height: 20),
              ],
              if (nota['observaciones_clinicas'] != null && nota['observaciones_clinicas'].toString().isNotEmpty) ...[
                _buildSectionDetail('Observaciones Clínicas', nota['observaciones_clinicas'] ?? ''),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _buildSectionDetail(String label, String content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label.toUpperCase(),
          style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            color: Color(0xFF10B981),
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          content,
          style: const TextStyle(fontSize: 13, height: 1.4),
        ),
      ],
    );
  }

  Widget _buildRecomendacionesTab(bool isDark) {
    if (_recomendaciones.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.rule_folder_outlined, size: 64, color: Colors.grey),
            const SizedBox(height: 12),
            Text(
              'Sin recomendaciones vigentes.',
              style: TextStyle(color: isDark ? Colors.grey[400] : Colors.grey[600], fontSize: 14),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _recomendaciones.length,
      itemBuilder: (context, index) {
        final rec = _recomendaciones[index];
        final desc = rec['descripcion'] ?? {};
        final titulo = desc['titulo'] ?? 'Recomendación';
        final detalle = desc['detalle'] ?? '';
        final categoria = rec['categoria'] ?? '';

        IconData catIcon = Icons.info_outline;
        if (categoria == 'hidratacion') catIcon = Icons.local_drink;
        if (categoria == 'actividad_fisica') catIcon = Icons.fitness_center;

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          color: isDark ? const Color(0xFF1C1D24) : Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  backgroundColor: Colors.blue.withValues(alpha: 0.1),
                  child: Icon(catIcon, color: const Color(0xFF10B981)),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        titulo,
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        detalle,
                        style: TextStyle(
                          fontSize: 12,
                          height: 1.3,
                          color: isDark ? Colors.grey[300] : Colors.grey[700],
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Asignada el: ${rec['fecha']}',
                        style: const TextStyle(fontSize: 10, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(48),
        child: Container(
          color: isDark ? const Color(0xFF1C1D24) : Colors.white,
          child: TabBar(
            controller: _innerTabController,
            indicatorColor: const Color(0xFF10B981),
            labelColor: const Color(0xFF10B981),
            unselectedLabelColor: Colors.grey,
            tabs: const [
              Tab(text: 'Consultas'),
              Tab(text: 'Recomendaciones'),
            ],
          ),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF10B981)))
          : _errorMsg != null
              ? Center(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(24),
                    child: Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: isDark ? const Color(0xFF111827) : Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: isDark ? Colors.white.withValues(alpha: 0.04) : Colors.grey[200]!,
                        ),
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.wifi_off_rounded, color: Colors.redAccent, size: 44),
                          const SizedBox(height: 12),
                          Text(
                            _errorMsg!,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 13,
                              height: 1.4,
                              color: isDark ? Colors.grey[300] : const Color(0xFF4B5563),
                            ),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            onPressed: _cargarDatos,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF10B981),
                              foregroundColor: Colors.white,
                              elevation: 0,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            icon: const Icon(Icons.refresh_rounded, size: 18),
                            label: const Text('Reintentar', style: TextStyle(fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                    ),
                  ),
                )
              : TabBarView(
                  controller: _innerTabController,
                  children: [
                    _buildNotasTab(isDark),
                    _buildRecomendacionesTab(isDark),
                  ],
                ),
    );
  }
}
