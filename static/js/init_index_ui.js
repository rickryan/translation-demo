document.addEventListener('DOMContentLoaded', (event) => {
    fetch('/${site_id}/languages')
        .then(response => response.json())
        .then(languages => {
            const populateSelect = (selectId) => {
                const selectElement = document.getElementById(selectId);
                selectElement.innerHTML = '';
                languages.forEach(language => {
                    const option = document.createElement('option');
                    option.value = language.code;
                    option.textContent = language.name;
                    selectElement.appendChild(option);
                });
                // Refresh the bootstrap-select UI
                $('.selectpicker').selectpicker('refresh');
            };

            populateSelect('languageSelector');

        })
        .catch(error => console.error('Error fetching languages:', error));
});