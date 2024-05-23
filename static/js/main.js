$(document).ready(function () {
  // Verifica si ya se ha seleccionado un modo previamente
  const savedMode = localStorage.getItem('mode');

  // Aplica el modo guardado si existe, o establece el modo de día como predeterminado
  if (savedMode === 'night-mode') {
    $('body').addClass('night-mode');
  } else {
    $('body').addClass('day-mode');

  }

  // Al hacer clic en el botón de cambio de modo
  $('#toggle-mode').click(function () {
    // Alterna las clases CSS en el elemento <body>
    $('body').toggleClass('day-mode night-mode');

    // Guarda la preferencia de modo en una cookie
    const currentMode = $('body').hasClass('night-mode') ? 'night-mode' : 'day-mode';
    localStorage.setItem('mode', currentMode);
  });
});
