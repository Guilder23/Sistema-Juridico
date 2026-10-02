function abrirModalEliminarReporte(id) {
    document.getElementById('formEliminarReporte').action = `/reportes/eliminar/${id}/`;
    openModal('modalEliminarReporte');
}
