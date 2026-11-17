--[[ KOReader user patch: show the current reading session length in the status bar.

Adds "Session h:mm" as the status bar's "External content" item. A session starts when the
book is opened or the device wakes from sleep (the Statistics plugin's start_current_period),
so the time includes pauses while the screen stays on. Nothing is shown if Statistics is off.
--]]
local ReaderFooter = require("apps/reader/modules/readerfooter")

local orig_init = ReaderFooter.init
function ReaderFooter:init(...)
    orig_init(self, ...)
    self:addAdditionalFooterContent(function()
        local stats = self.ui and self.ui.statistics
        local start = stats and stats.settings and stats.settings.is_enabled and stats.start_current_period
        if not start or start == 0 then return end
        local mins = math.floor((os.time() - start) / 60)
        return string.format("Session %d:%02d", math.floor(mins / 60), mins % 60)
    end)
end
