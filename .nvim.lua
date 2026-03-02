vim.api.nvim_create_autocmd("FileType", {
    pattern = { "c", "cpp", "cmake" },
    callback = function()
        vim.opt_local.colorcolumn = "120"
    end,
})
