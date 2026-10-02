function abrirModalEditarUsuario(btn) {
    const d = btn.dataset;
    document.getElementById('formEditarUsuario').action = `/usuarios/editar/${d.id}/`;
    document.getElementById('edit_user_username').value = d.username || '';
    document.getElementById('edit_user_first_name').value = d.firstname || '';
    document.getElementById('edit_user_last_name').value = d.lastname || '';
    document.getElementById('edit_user_email').value = d.email || '';
    document.getElementById('edit_user_rol').value = d.rol || 'GESTOR';
    document.getElementById('edit_user_telefono').value = d.telefono || '';
    document.getElementById('edit_user_cargo').value = d.cargo || '';
    openModal('modalEditarUsuario');
}

function abrirModalEliminarUsuario(btn) {
    const d = btn.dataset;
    document.getElementById('formEliminarUsuario').action = `/usuarios/eliminar/${d.id}/`;
    document.getElementById('delete_username_label').textContent = d.username || '';
    openModal('modalEliminarUsuario');
}
