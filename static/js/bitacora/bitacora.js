function abrirModalEliminarBitacora(id) {
    document.getElementById('formEliminarBitacora').action = `/bitacora/eliminar/${id}/`;
    openModal('modalEliminarBitacora');
}
