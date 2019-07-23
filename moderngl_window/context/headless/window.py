import moderngl

from moderngl_window.context.base import BaseWindow
from moderngl_window.context.headless.keys import Keys


class Window(BaseWindow):
    """Headless window.

    Do not currently support any form window events or key input.
    """
    keys = Keys

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._fbo = None
        self._vsync = False  # We don't care about vsync in headless mode
        self._resizable = False  # headless window is not resizable
        self._cursor = False  # Headless don't have a cursor
        self.init_mgl_context()
        self.set_default_viewport()

    @property
    def fbo(self) -> moderngl.Framebuffer:
        """moderngl.Framebuffer: The default framebuffer"""
        return self._fbo

    def init_mgl_context(self) -> None:
        """Create an standalone context and framebuffer"""
        self._ctx = moderngl.create_standalone_context(require=self.gl_version_code)
        self._fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture(self.size, 4, samples=self._samples),
            depth_attachment=self.ctx.depth_texture(self.size),
        )
        self.use()

    def use(self):
        """Bind the window's framebuffer"""
        self._fbo.use()

    def clear(self, red=0.0, green=0.0, blue=0.0, alpha=0.0, depth=1.0, viewport=None):
        """
        Clear the default framebuffer

        Args:
            red (float): color component
            green (float): color component
            blue (float): color component
            alpha (float): alpha component
            depth (float): depth value
            viewport (tuple): The viewport
        """
        self._fbo.clear(red=red, green=green, blue=blue, alpha=alpha, depth=depth, viewport=viewport)

    def swap_buffers(self) -> None:
        """
        Placeholder. We currently don't do double buffering in headless mode.
        This may change in the future.
        """
        # TODO: No double buffering currently
        self._frames += 1

    def destroy(self) -> None:
        # TODO: A context can currently not be invaldiated in ModernGL
        pass
