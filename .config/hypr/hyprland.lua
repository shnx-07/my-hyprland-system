-- ============================================================
-- HYPRLAND.LUA
-- ============================================================
--
-- Sections:
--   01. AUTOSTART
--   02. ENVIRONMENT
--   03. THEME
--   04. FONT
--   05. ANIMATIONS
--   06. DECORATION
--   07. KEYBOARD
--   08. MOUSE
--   09. KEYBINDS
--   10. LAYOUTS
--   11. RULES
--   12. MONITORS
--   13. SESSION KEYBINDS
--   14. HYPRGLASS
--

colors = {
	bg0 = "#1e1e2e", -- main background
	bg1 = "#181825", -- darker background
	fg = "#cdd6f4", -- main text
	accent = "#89b4fa", -- primary accent
	accent_alt = "#74c7ec", -- secondary accent
}

-- ============================================================
-- 01. AUTOSTART
-- ============================================================

hl.on("hyprland.start", function()
	hl.exec_cmd("wpaperd -d") -- hl.exec_cmd("waybar & wpaperd -d")
	hl.exec_cmd("hyprpaper")
	hl.exec_cmd("playerctld daemon")
	hl.exec_cmd("systemctl --user start hyprpolkitagent")
	hl.exec_cmd("wl-paste --type text --watch cliphist store &")
	hl.exec_cmd("wl-paste --type image --watch cliphist store &")
	hl.exec_cmd("hyprpm reload")
	hl.exec_cmd("hypridle")
end)

-- ============================================================
-- 02. ENVIRONMENT
-- ============================================================

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")

-- ============================================================
-- 03. THEME
-- ============================================================
--
-- Priority order:
--   1. manual_theme  -- set in DECORATION to override
--   2. wallpaper colors -- auto-extracted via matugen / pywal / wallust
--   3. fallback palette -- built-in gradient
--

local function load_dynamic_theme()
	local cache = (os.getenv("HOME") or "~") .. "/.cache"
	local paths = {
		cache .. "/hypr/colors.lua",
		cache .. "/wal/colors.lua",
		cache .. "/matugen/colors.lua",
	}
	for _, path in ipairs(paths) do
		local chunk = loadfile(path)
		if chunk then
			local ok, colors = pcall(chunk)
			if ok and type(colors) == "table" and colors.active_border then
				return colors
			end
		end
	end
	return nil
end

local default_theme = {
	active_border = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 },
	inactive_border = "rgba(595959aa)",
	bell_border = "rgba(ff5555ee)",
}

THEME = {
	resolve = function(manual_theme)
		if manual_theme and type(manual_theme) == "table" and manual_theme.active_border then
			return manual_theme
		end
		return load_dynamic_theme() or default_theme
	end,
}

-- ============================================================
-- 04. FONT
-- ============================================================
--
-- Sizes apply per section: main, bar, launcher, notification, terminal
--

local active_font = {
	family = "Inter",
	sizes = {
		main = 11,
		bar = 10,
		launcher = 12,
		notification = 10,
		terminal = 11,
	},
}

FONT = {
	config = active_font,
	resolve = function(user_font)
		if type(user_font) == "table" then
			if user_font.family then
				active_font.family = user_font.family
			end
			if type(user_font.sizes) == "table" then
				for section, size in pairs(user_font.sizes) do
					active_font.sizes[section] = size
				end
			end
		end
		FONT.config = active_font
		return active_font
	end,
}

-- ============================================================
-- 05. ANIMATIONS
-- ============================================================

-- Bezier / spring curves
hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })
hl.curve("easeInOutCubic", { type = "bezier", points = { { 0.65, 0.05 }, { 0.36, 1 } } })
hl.curve("linear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.curve("almostLinear", { type = "bezier", points = { { 0.5, 0.5 }, { 0.75, 1 } } })
hl.curve("quick", { type = "bezier", points = { { 0.15, 0 }, { 0.1, 1 } } })
hl.curve("easy", { type = "spring", mass = 1, stiffness = 71.2633, dampening = 15.8273644 })

hl.config({ animations = { enabled = true } })

-- Windows
hl.animation({ leaf = "global", enabled = true, speed = 10, bezier = "default" })
hl.animation({ leaf = "border", enabled = true, speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows", enabled = true, speed = 5, spring = "easy" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 4.1, spring = "easy", style = "popin 87%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 3, spring = "easy", style = "popin 87%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 5, bezier = "easeOutQuint" })

-- Fade
hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade", enabled = true, speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 1.79, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.39, bezier = "almostLinear" })

-- Layers
-- hl.animation({ leaf = "layers",    enabled = true, speed = 3.81, bezier = "easeOutQuint"            })
-- hl.animation({ leaf = "layersIn",  enabled = true, speed = 4,    bezier = "easeOutQuint", style = "fade" })
-- hl.animation({ leaf = "layersOut", enabled = true, speed = 1.5,  bezier = "linear",       style = "fade" })

-- Workspaces (slide)
hl.animation({ leaf = "workspaces", enabled = true, speed = 5, bezier = "easeOutQuint", style = "slide" })
hl.animation({ leaf = "workspacesIn", enabled = true, speed = 5, bezier = "easeOutQuint", style = "slide" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 5, bezier = "easeOutQuint", style = "slide" })

-- Misc
hl.animation({ leaf = "zoomFactor", enabled = true, speed = 7, bezier = "quick" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 5, bezier = "easeOutQuint" })

-- ============================================================
-- 06. DECORATION
-- ============================================================
--
-- Edit visual_settings below to change theme, font, gaps, borders, blur, shadows.
--

local visual_settings = {

	-- Theme: nil = auto from wallpaper, set a table to override
	manual_theme = nil,
	-- manual_theme = {
	--     active_border   = { colors = { "rgba(ff79c6ee)", "rgba(bd93f9ee)" }, angle = 45 },
	--     inactive_border = "rgba(44475aaa)",
	-- },

	-- Font
	font = {
		family = "Inter",
		sizes = { main = 11, bar = 10, launcher = 12, notification = 10, terminal = 11 },
	},

	-- Gaps & borders
	gaps_in = 5,
	gaps_out = 10,
	border_size = 0, -- must be > 0 for resize_on_border to work
	rounding = 10,
	rounding_power = 2,

	-- Opacity
	active_opacity = 1.0,
	inactive_opacity = 0.85,

	-- Shadow
	shadow = {
		enabled = true,
		range = 15,
		render_power = 3,
		color = "rgba(00000040)",
	},

	-- Blur
	blur = {
		enabled = true,
		size = 3,
		passes = 1,
		vibrancy = 0.1696,
	},
}

local active_colors = THEME.resolve(visual_settings.manual_theme)
local resolved_font = FONT.resolve(visual_settings.font)

hl.config({
	general = {
		gaps_in = visual_settings.gaps_in,
		gaps_out = visual_settings.gaps_out,
		border_size = visual_settings.border_size,

		col = {
			active_border = active_colors.active_border,
			inactive_border = active_colors.inactive_border,
		},

		resize_on_border = true,
		allow_tearing = false,
		layout = "dwindle",
	},

	decoration = {
		rounding = visual_settings.rounding,
		rounding_power = visual_settings.rounding_power,
		active_opacity = visual_settings.active_opacity,
		inactive_opacity = visual_settings.inactive_opacity,

		shadow = visual_settings.shadow,
		blur = visual_settings.blur,
	},
})

-- ============================================================
-- 07. KEYBOARD
-- ============================================================

hl.config({
	input = {
		kb_layout = "us",
		kb_variant = "",
		kb_model = "",
		kb_options = "",
		kb_rules = "",

		repeat_rate = 25,
		repeat_delay = 300,
	},
})

-- ============================================================
-- 08. MOUSE
-- ============================================================

hl.config({
	input = {
		follow_mouse = 1,
		sensitivity = 0,

		touchpad = {
			natural_scroll = true,
		},
	},
})

-- Three-finger horizontal swipe -> switch workspace
hl.gesture({
	fingers = 3,
	direction = "horizontal",
	action = "workspace",
})

-- ============================================================
-- 09. KEYBINDS
-- ============================================================

local MOD = "SUPER"

-- Applications
local terminal = "kitty"
local fileManager = "nemo"
local launcher = "rofi -show drun -show-icons"
local runner = "rofi -show run"
local browser = "xdg-open https:// || firefox || zen-browser"
local music = "spotify"

hl.bind(MOD .. " + Return", hl.dsp.exec_cmd(terminal))
hl.bind(MOD .. " + SPACE", hl.dsp.exec_cmd(launcher))
hl.bind(MOD .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(MOD .. " + B", hl.dsp.exec_cmd(browser))
hl.bind(MOD .. " + M", hl.dsp.exec_cmd(music))
hl.bind(MOD .. " + SHIFT+ SPACE", hl.dsp.exec_cmd(runner))

-- Screenshot & clipboard
hl.bind(MOD .. " + SHIFT+ S", hl.dsp.exec_cmd('grim -g "$(slurp)" - | swappy -f -'))
hl.bind(
	MOD .. " + SHIFT+ V",
	hl.dsp.exec_cmd("cliphist list | rofi -dmenu -display-columns 2 | cliphist decode | wl-copy")
)
hl.bind("Print", hl.dsp.exec_cmd('grim -g "$(slurp)" - | wl-copy || hyprshot -m region'))

-- Window management
hl.bind(MOD .. " + Q", hl.dsp.window.close())
hl.bind(MOD .. " + F", hl.dsp.window.fullscreen(mode == 1))
hl.bind(MOD .. " + T", hl.dsp.window.float({ action = "toggle" }))
hl.bind(MOD .. " + P", hl.dsp.window.pseudo())

-- Mouse: SUPER + LMB = drag, SUPER + RMB = resize
hl.bind(MOD .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(MOD .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Focus (Vim HJKL + Arrow keys)
hl.bind(MOD .. " + h", hl.dsp.focus({ direction = "left" }))
hl.bind(MOD .. " + j", hl.dsp.focus({ direction = "down" }))
hl.bind(MOD .. " + k", hl.dsp.focus({ direction = "up" }))
hl.bind(MOD .. " + l", hl.dsp.focus({ direction = "right" }))
hl.bind(MOD .. " + left", hl.dsp.focus({ direction = "left" }))
hl.bind(MOD .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(MOD .. " + up", hl.dsp.focus({ direction = "up" }))
hl.bind(MOD .. " + down", hl.dsp.focus({ direction = "down" }))

-- Move window (SHIFT + Vim HJKL + Arrow keys)
hl.bind(MOD .. " + SHIFT + h", hl.dsp.window.move({ direction = "left" }))
hl.bind(MOD .. " + SHIFT + j", hl.dsp.window.move({ direction = "down" }))
hl.bind(MOD .. " + SHIFT + k", hl.dsp.window.move({ direction = "up" }))
hl.bind(MOD .. " + SHIFT + l", hl.dsp.window.move({ direction = "right" }))
hl.bind(MOD .. " + SHIFT + left", hl.dsp.window.move({ direction = "left" }))
hl.bind(MOD .. " + SHIFT + right", hl.dsp.window.move({ direction = "right" }))
hl.bind(MOD .. " + SHIFT + up", hl.dsp.window.move({ direction = "up" }))
hl.bind(MOD .. " + SHIFT + down", hl.dsp.window.move({ direction = "down" }))

-- Workspace access (1-9, 0 = workspace 10)
for workspace = 1, 10 do
	local key = (workspace == 10) and 0 or workspace
	hl.bind(MOD .. " + " .. key, hl.dsp.focus({ workspace = workspace }))
	hl.bind(MOD .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = workspace }))
end

-- Workspace cycling
hl.bind(MOD .. " + TAB", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(MOD .. " + SHIFT + TAB", hl.dsp.focus({ workspace = "e-1" }))
hl.bind(MOD .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(MOD .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))

-- Special workspace
hl.bind(MOD .. " + S", hl.dsp.workspace.toggle_special("magic"))

-- System utilities
--hl.bind(MOD .. " + SHIFT + B", hl.dsp.exec_cmd("killall -SIGUSR1 waybar || waybar"))
hl.bind(MOD .. " + G", hl.dsp.exec_cmd("hyprctl dispatch workspaceopt allgaps toggle"))
hl.bind(MOD .. " + N", hl.dsp.exec_cmd("swaync-client -t"))
hl.bind(MOD .. " + SHIFT + C", hl.dsp.exec_cmd("hyprctl reload"))

-- Media keys
hl.bind(
	"XF86AudioRaiseVolume",
	hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioLowerVolume",
	hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioMute",
	hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioMicMute",
	hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),
	{ locked = true, repeating = true }
)
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"), { locked = true, repeating = true })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })

-- ============================================================
-- 10. LAYOUTS
-- ============================================================

hl.config({
	dwindle = {
		preserve_split = true,
	},

	master = {
		new_status = "master",
	},

	scrolling = {
		fullscreen_on_one_column = true,
	},

	misc = {
		force_default_wallpaper = -1,
		disable_hyprland_logo = false,
		animate_manual_resizes = true,
		animate_mouse_windowdragging = true,
	},
})

-- ============================================================
-- 11. RULES
-- ============================================================

-- Suppress maximize requests from all apps
hl.window_rule({
	name = "suppress-maximize-events",
	match = { class = ".*" },
	suppress_event = "maximize",
})

-- Fix XWayland drag issues
hl.window_rule({
	name = "fix-xwayland-drags",
	match = {
		class = "^$",
		title = "^$",
		xwayland = true,
		float = true,
		fullscreen = false,
		pin = false,
	},
	no_focus = true,
})

-- Float and position hyprland-run
hl.window_rule({
	name = "move-hyprland-run",
	match = { class = "hyprland-run" },
	move = "20 monitor_h-120",
	float = true,
})

-- ============================================================
-- 12. MONITORS
-- ============================================================
-- Run `hyprctl monitors` to get output names for your displays.
-- See: https://wiki.hypr.land/Configuring/Basics/Monitors/

-- Laptop screen
hl.monitor({
	output = "eDP-1",
	mode = "preferred",
	position = "auto",
	scale = 1,
})

-- External monitor
hl.monitor({
	output = "HDMI-A-1",
	mode = "2560x1440@144",
	position = "auto",
	scale = 1,
})

-- HDMI connected: disable laptop screen
hl.on("monitor.added", function(monitor)
	if monitor.name == "HDMI-A-1" then
		hl.monitor({
			output = "eDP-1",
			disabled = true,
		})
	end
end)

-- HDMI disconnected: enable laptop screen
hl.on("monitor.removed", function(monitor)
	if monitor.name == "HDMI-A-1" then
		hl.monitor({
			output = "eDP-1",
			mode = "preferred",
			position = "auto",
			scale = 1,
			disabled = false,
		})
	end
end)

-- ------------------------------------------------------------
-- SESSION KEYBINDS
-- ------------------------------------------------------------

-- Lock screen (SUPER+L is taken by focus-right – use SUPER+SHIFT+L)
hl.bind(MOD .. " + SHIFT + L", hl.dsp.exec_cmd("hyprlock || swaylock"))

-- Power Menu / Exit
hl.bind(MOD .. " + Escape", hl.dsp.exec_cmd("wlogout || hyprshutdown"))

-- Logout
hl.bind(MOD .. " + SHIFT + M", hl.dsp.exit())

-- Shutdown and reboot via systemd
hl.bind(MOD .. " + SHIFT + P", hl.dsp.exec_cmd("systemctl poweroff"))
hl.bind(MOD .. " + SHIFT + R", hl.dsp.exec_cmd("systemctl reboot"))

-- ============================================================
-- 14. HYPRGLASS
-- ============================================================
-- Liquid Glass effect: frosted blur, edge refraction, chromatic
-- aberration, specular highlights on transparent windows.
--
-- Install:
--   hyprpm add https://github.com/hyprnux/hyprglass
--   hyprpm enable hyprglass
--
-- The plugin must be loaded before this block runs.
-- The `if hl.plugin.hyprglass then` guard makes it safe to
-- keep this config even when the plugin is not installed.
--
if hl.plugin.hyprglass then
	local hg = hl.plugin.hyprglass

	hg.preset("clear", {
		glass_opacity = 0.8,
		blur_strength = 1.0,
		dark = { brightness = 0.82 },
		light = { brightness = 1.2 },
	})

	hg.preset("contrasted", {
		inherits = "high_contrast",
		contrast = 1.2,
		adaptive_dim = 1.0,
		dark = { tint_color = 0x02142aa9 },
	})

	local function tint(c, alpha)
		return tonumber(c:match("%x%x%x%x%x%x"), 16) * 256 + math.floor(alpha * 255 + 0.5)
	end

	hg.preset("glass", {
		blur_strength = 1.5,
		blur_iterations = 3,
		chromatic_aberration = 0.8,
		fresnel_strength = 0.8,
		edge_thickness = 0.08,
		tint_color = tint(colors.bg0, 0.12),
		lens_distortion = 0.9,
		brightness = 1.0,
		contrast = 1.7,
		saturation = 1,
		vibrancy = 0.8,
		vibrancy_darkness = 1,
		adaptive_boost = 0.5,
	})

	hg.preset("apple", {
		blur_strength = 2.2,
		blur_iterations = 3,
		refraction_strength = 0.55,
		chromatic_aberration = 0.3,
		fresnel_strength = 0.5,
		specular_strength = 0.75,
		edge_thickness = 0.05,
		lens_distortion = 0.3,
		dark = {
			brightness = 0.82,
			contrast = 0.90,
			saturation = 0.80,
			vibrancy = 0.15,
			adaptive_dim = 0.4,
		},
		light = {
			brightness = 1.12,
			contrast = 0.92,
			saturation = 0.85,
			vibrancy = 0.12,
			adaptive_boost = 0.4,
		},
	})

	hg.config({
		enabled = true,
		default_theme = "dark",
		default_preset = "apple",
		layers = { enabled = true },
	})
end
