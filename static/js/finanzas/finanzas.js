function abrirModalPagarCuota(btn) {
    const d = btn.dataset;
    document.getElementById('formPagarCuota').action = `/finanzas/cuota/pagar/${d.cuotaid}/`;
    document.getElementById('lblNumeroCuota').textContent = `Cuota #${d.numero}`;
    document.getElementById('lblTituloPlan').textContent = d.plantitulo || '';
    document.getElementById('pay_monto_pagado').value = d.monto || '';
    document.getElementById('pay_fecha_pago').value = new Date().toISOString().split('T')[0];
    openModal('modalPagarCuota');
}
