(function () {
  function normalize(text) {
    return (text || '').toLowerCase().trim();
  }

  // Filters <tbody> rows of a table against free-text input. Rows with class
  // "row-detail" (e.g. an expandable admin panel under a parent row) are not
  // matched individually — they follow their preceding row's visibility instead.
  function enableTableSearch(input, table) {
    if (!input || !table || !table.tBodies[0]) return;
    var tbody = table.tBodies[0];
    input.addEventListener('input', function () {
      var q = normalize(input.value);
      Array.prototype.forEach.call(tbody.rows, function (row) {
        if (row.classList.contains('row-detail')) return;
        var text = normalize(row.textContent);
        var match = !q || text.indexOf(q) !== -1;
        row.style.display = match ? '' : 'none';
        var next = row.nextElementSibling;
        if (next && next.classList.contains('row-detail') && !match) {
          next.style.display = 'none';
        }
      });
    });
  }

  // Click-to-sort column headers. Numeric-aware; blanks/— sort last.
  function enableTableSort(table) {
    if (!table || !table.tHead || !table.tBodies[0]) return;
    var tbody = table.tBodies[0];
    var headers = table.tHead.rows[0].cells;

    Array.prototype.forEach.call(headers, function (th, index) {
      if (th.classList.contains('no-sort')) return;
      th.classList.add('sortable');
      th.addEventListener('click', function () {
        var asc = th.dataset.sortDir !== 'asc';
        Array.prototype.forEach.call(headers, function (h) {
          delete h.dataset.sortDir;
          h.classList.remove('sorted-asc', 'sorted-desc');
        });
        th.dataset.sortDir = asc ? 'asc' : 'desc';
        th.classList.add(asc ? 'sorted-asc' : 'sorted-desc');

        var rows = Array.prototype.slice.call(tbody.rows);
        var numeric = rows.every(function (row) {
          var cell = row.cells[index];
          var t = cell ? cell.textContent.trim() : '';
          return t === '' || t === '—' || !isNaN(parseFloat(t.replace(/,/g, '')));
        });

        rows.sort(function (a, b) {
          var av = a.cells[index] ? a.cells[index].textContent.trim() : '';
          var bv = b.cells[index] ? b.cells[index].textContent.trim() : '';
          if (numeric) {
            var an = parseFloat(av.replace(/,/g, ''));
            var bn = parseFloat(bv.replace(/,/g, ''));
            if (isNaN(an)) an = asc ? Infinity : -Infinity;
            if (isNaN(bn)) bn = asc ? Infinity : -Infinity;
            return asc ? an - bn : bn - an;
          }
          return asc ? av.localeCompare(bv) : bv.localeCompare(av);
        });
        rows.forEach(function (row) { tbody.appendChild(row); });
      });
    });
  }

  // Filters a list of card-like elements (not plain table rows) by free-text input.
  function enableCardSearch(input, container, cardSelector, matchSelector) {
    if (!input || !container) return;
    input.addEventListener('input', function () {
      var q = normalize(input.value);
      container.querySelectorAll(cardSelector).forEach(function (card) {
        var target = matchSelector ? card.querySelector(matchSelector) : card;
        var text = normalize(target ? target.textContent : card.textContent);
        card.style.display = (!q || text.indexOf(q) !== -1) ? '' : 'none';
      });
    });
  }

  window.TableTools = {
    enableTableSearch: enableTableSearch,
    enableTableSort: enableTableSort,
    enableCardSearch: enableCardSearch,
  };
})();
