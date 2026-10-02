function abrirModalEliminarDocumento(id, titulo) {
    document.getElementById('formEliminarDocumento').action = `/documentos/eliminar/${id}/`;
    document.getElementById('delete_titulo_documento').textContent = titulo;
    openModal('modalEliminarDocumento');
}
