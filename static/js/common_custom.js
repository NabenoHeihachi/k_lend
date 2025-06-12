const prevent_submit_enter_forms = document.getElementsByClassName("prevent-forms-submit-enter");
const prevent_double_click_forms = document.getElementsByClassName("prevent-double-click-form");
const prevent_double_click_buttons = document.getElementsByClassName("prevent-double-click-button");

Array.from(prevent_submit_enter_forms).forEach((prevent_submit_enter_form) => {
    prevent_submit_enter_form.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            // alert("エンターで送信することはできません");
            event.preventDefault();
        }
    });
});

Array.from(prevent_double_click_forms).forEach((prevent_double_click_form) => {
    prevent_double_click_form.addEventListener('submit', (event) => {
        Array.from(prevent_double_click_buttons).forEach((prevent_double_click_button) => {
                // ボタンを無効化
                prevent_double_click_button.disabled = true;
                prevent_double_click_button.textContent = '送信中...';
        });
    });
});

