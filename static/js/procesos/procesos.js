function abrirModalEditarProceso(btn) {
    const d = btn.dataset;
    document.getElementById('formEditarProceso').action = `/procesos/editar/${d.id}/`;
    document.getElementById('edit_proceso_titulo').value = d.titulo || '';
    document.getElementById('edit_proceso_descripcion').value = d.descripcion || '';
    document.getElementById('edit_proceso_estado').value = d.estado || 'EN_PROCESO';
    document.getElementById('edit_proceso_prioridad').value = d.prioridad || 'MEDIA';
    document.getElementById('edit_proceso_responsable').value = d.responsable || '';
    document.getElementById('edit_proceso_inicio').value = d.inicio || '';
    document.getElementById('edit_proceso_limite').value = d.limite || '';
    document.getElementById('edit_proceso_obs').value = d.observaciones || '';
    openModal('modalEditarProceso');
}

function abrirModalEliminarProceso(btn) {
    const d = btn.dataset;
    document.getElementById('formEliminarProceso').action = `/procesos/eliminar/${d.id}/`;
    document.getElementById('delete_titulo_proceso').textContent = d.titulo || '';
    openModal('modalEliminarProceso');
}
