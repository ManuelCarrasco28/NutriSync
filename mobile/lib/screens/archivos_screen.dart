import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';

class ArchivosScreen extends StatefulWidget {
  const ArchivosScreen({super.key});

  @override
  State<ArchivosScreen> createState() => _ArchivosScreenState();
}

class _ArchivosScreenState extends State<ArchivosScreen> {
  bool _loading = false;
  List<dynamic> _archivos = [];
  String? _errorMsg;

  @override
  void initState() {
    super.initState();
    _cargarDatos();
  }

  Future<void> _cargarDatos() async {
    setState(() {
      _loading = true;
      _errorMsg = null;
    });

    try {
      final archivosData = await ApiService.getArchivos();
      if (mounted) {
        setState(() {
          _archivos = archivosData;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMsg = 'Error al cargar los documentos.';
          _loading = false;
          _cargarDatosMock();
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(_errorMsg ?? 'Error al conectar.')),
        );
      }
    }
  }

  void _cargarDatosMock() {
    _archivos = [
      {
        'id': 1,
        'nombre': 'Analisis de Sangre - Hemograma Completo.pdf',
        'categoria': 'Laboratorios',
        'fecha_registro': '2026-07-09',
        'archivo_url': '/media/pacientes/archivos/hemograma.pdf',
        'observaciones': 'Valores de glucosa y colesterol dentro de los rangos normales.'
      },
      {
        'id': 2,
        'nombre': 'Recetario de Suplementacion Deportiva.pdf',
        'categoria': 'Documentos',
        'fecha_registro': '2026-07-08',
        'archivo_url': '/media/pacientes/archivos/suplementacion.pdf',
        'observaciones': 'Tomar creatina post-entrenamiento e infusiones indicadas.'
      }
    ];
  }

  void _verArchivo(Map<String, dynamic> archivo) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Text(archivo['nombre'] ?? 'Documento'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Categoría: ${archivo['categoria']}', style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text('Fecha: ${archivo['fecha_registro']}'),
              const SizedBox(height: 8),
              if (archivo['observaciones'].toString().isNotEmpty) ...[
                const Text('Observaciones del Nutricionista:', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(archivo['observaciones']),
                const SizedBox(height: 12),
              ],
              const Text(
                'Nota: En una versión de producción con certificado SSL activo, este archivo se descargaría y abriría directamente en tu visor de PDFs del celular.',
                style: TextStyle(fontSize: 10, color: Colors.grey, fontStyle: FontStyle.italic),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cerrar', style: TextStyle(color: Color(0xFF10B981))),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis Documentos y Archivos'),
        backgroundColor: isDark ? const Color(0xFF111827) : const Color(0xFF10B981),
        foregroundColor: Colors.white,
        elevation: 0,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(bottom: Radius.circular(18)),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF10B981)))
          : _archivos.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.folder_open_outlined, size: 64, color: Colors.grey),
                      const SizedBox(height: 12),
                      Text(
                        'No tienes documentos compartidos todavía.',
                        style: TextStyle(color: isDark ? Colors.grey[400] : Colors.grey[600], fontSize: 14),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _archivos.length,
                  itemBuilder: (context, index) {
                    final archivo = _archivos[index];
                    final categoria = archivo['categoria'] ?? 'Otros';
                    
                    IconData fileIcon = Icons.insert_drive_file_outlined;
                    if (categoria == 'Laboratorios') fileIcon = Icons.biotech_outlined;
                    if (categoria == 'Documentos') fileIcon = Icons.description_outlined;
                    if (categoria == 'Fotos de Progreso') fileIcon = Icons.image_outlined;

                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      color: isDark ? const Color(0xFF1C1D24) : Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: const Color(0xFF10B981).withValues(alpha: 0.1),
                          child: Icon(fileIcon, color: const Color(0xFF10B981)),
                        ),
                        title: Text(
                          archivo['nombre'] ?? 'Archivo',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        subtitle: Text(
                          '$categoria — ${archivo['fecha_registro']}',
                          style: const TextStyle(fontSize: 12),
                        ),
                        trailing: const Icon(Icons.download_for_offline_outlined, color: Color(0xFF10B981)),
                        onTap: () => _verArchivo(archivo),
                      ),
                    );
                  },
                ),
    );
  }
}
