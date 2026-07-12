import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';

class MedidasTab extends StatefulWidget {
  const MedidasTab({super.key});

  @override
  State<MedidasTab> createState() => _MedidasTabState();
}

class _MedidasTabState extends State<MedidasTab> {
  bool _loading = false;
  List<dynamic> _medidas = [];
  String? _errorMsg;

  @override
  void initState() {
    super.initState();
    _cargarMedidas();
  }

  Future<void> _cargarMedidas() async {
    setState(() {
      _loading = true;
      _errorMsg = null;
    });

    try {
      final medidas = await ApiService.getMedidas();
      if (mounted) {
        setState(() {
          _medidas = medidas;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMsg = 'No se pudieron cargar las medidas corporales. Verifica tu conexión.';
          _loading = false;
        });
      }
    }
  }

  Widget _buildGridCol(String label, String value, isDark) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: isDark ? Colors.grey[400] : const Color(0xFF6B7280),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textThemeColor = isDark ? Colors.white : const Color(0xFF1F2937);

    if (_loading && _medidas.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF10B981)),
      );
    }

    return RefreshIndicator(
      onRefresh: _cargarMedidas,
      color: const Color(0xFF10B981),
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        children: [
          Text(
            '📈 Historial de Progreso',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF10B981),
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 20),

          if (_errorMsg != null)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF111827) : Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isDark ? Colors.white.withValues(alpha: 0.04) : Colors.grey[200]!,
                ),
              ),
              child: Column(
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
                    onPressed: _cargarMedidas,
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
            )
          else if (_medidas.isEmpty)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: isDark
                      ? const [Color(0xFF111827), Color(0xFF1F2937)]
                      : const [Color(0xFFFFFFFF), Color(0xFFF7FBFF)],
                ),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isDark ? Colors.white.withValues(alpha: 0.04) : Colors.grey[200]!,
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: isDark ? 0.14 : 0.05),
                    blurRadius: 14,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Text(
                'No se registran medidas corporales cargadas aún en tu expediente.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: isDark ? Colors.grey[400] : const Color(0xFF6B7280),
                  fontStyle: FontStyle.italic,
                ),
              ),
            )
          else
            ..._medidas.map((medida) {
              final String fecha = medida['fecha'] ?? '';
              final double peso = (medida['peso_kg'] ?? 0.0).toDouble();
              final double imc = (medida['imc'] ?? 0.0).toDouble();
              final double? grasa = medida['grasa_corporal_pct'] != null ? (medida['grasa_corporal_pct']).toDouble() : null;
              final double? musculo = medida['masa_muscular_kg'] != null ? (medida['masa_muscular_kg']).toDouble() : null;
              final String? notas = medida['notas'] as String?;

              return Container(
                margin: const EdgeInsets.only(bottom: 14),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: isDark
                        ? const [Color(0xFF111827), Color(0xFF1F2937)]
                        : const [Color(0xFFFFFFFF), Color(0xFFF7FBFF)],
                  ),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isDark ? Colors.white.withValues(alpha: 0.04) : Colors.grey[200]!,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: isDark ? 0.14 : 0.05),
                      blurRadius: 14,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Header de la medición
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '📅 Medición $fecha',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF10B981),
                            fontSize: 14,
                          ),
                        ),
                        Text(
                          '$peso kg',
                          style: TextStyle(
                            fontWeight: FontWeight.w900,
                            fontSize: 15,
                            color: textThemeColor,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    const Divider(height: 1, color: Colors.white10),
                    const SizedBox(height: 12),

                    // Grilla de detalles
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildGridCol('IMC', '$imc', isDark),
                        _buildGridCol('Grasa %', grasa != null ? '$grasa%' : '—', isDark),
                        _buildGridCol('Músculo', musculo != null ? '$musculo kg' : '—', isDark),
                      ],
                    ),

                    if (notas != null && notas.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Text(
                        '📝 Notas: $notas',
                        style: TextStyle(
                          fontSize: 12,
                          fontStyle: FontStyle.italic,
                          color: isDark ? Colors.grey[400] : const Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }
}
