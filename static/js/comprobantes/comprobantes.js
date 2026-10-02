function abrirModalEliminarComprobante(id) {
    document.getElementById('formEliminarComprobante').action = `/comprobantes/eliminar/${id}/`;
    openModal('modalEliminarComprobante');
}
