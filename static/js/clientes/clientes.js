function abrirModalEditarCliente(btn) {
    const d = btn.dataset;
    document.getElementById('formEditarCliente').action = `/clientes/editar/${d.id}/`;
    document.getElementById('edit_nombre_razon_social').value = d.nombre || '';
    document.getElementById('edit_ci_nit').value = d.cinit || '';
    document.getElementById('edit_tipo_cliente').value = d.tipo || 'EMPRESA';
    document.getElementById('edit_empresa_relacionada').value = d.empresa || '';
    document.getElementById('edit_telefono').value = d.telefono || '';
    document.getElementById('edit_correo').value = d.correo || '';
    document.getElementById('edit_direccion').value = d.direccion || '';
    document.getElementById('edit_estado').value = d.estado || 'ACTIVO';
    document.getElementById('edit_observaciones').value = d.observaciones || '';
    openModal('modalEditarCliente');
}

function abrirModalEliminarCliente(btn) {
    const d = btn.dataset;
    document.getElementById('formEliminarCliente').action = `/clientes/eliminar/${d.id}/`;
    document.getElementById('delete_nombre_cliente').textContent = d.nombre || '';
    openModal('modalEliminarCliente');
}
