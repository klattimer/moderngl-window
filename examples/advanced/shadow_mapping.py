"""
Shadow mapping example from:
https://www.opengl-tutorial.org/intermediate-tutorials/tutorial-16-shadow-mapping/
"""
import math
from pathlib import Path
from pyrr import Matrix44

import moderngl
import moderngl_window
from moderngl_window import geometry
from moderngl_window.opengl.projection import Projection3D

from base import CameraWindow


class ShadowMapping(CameraWindow):
    title = "Shadow Mapping"
    resource_dir = (Path(__file__) / '../../resources').resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera.projection.update(near=1, far=1000)

        # Offscreen buffer
        offscreen_size = self.wnd.buffer_size  # 1024, 1024
        self.offscreen_depth = self.ctx.depth_texture(offscreen_size)
        self.offscreen_color = self.ctx.texture(offscreen_size, 4)

        self.offscreen = self.ctx.framebuffer(
            color_attachments=[self.offscreen_color],
            depth_attachment=self.offscreen_depth,
        )

        # Scene geometry
        self.floor = geometry.cube(size=(25.0, 1.0, 25.0))
        self.wall = geometry.cube(size=(1.0, 5, 25), center=(-12.5, 2, 0))

        # Debug geometry
        self.offscreen_quad = geometry.quad_2d(size=(0.5, 0.5), pos=(0.75, 0.75))
        self.offscreen_quad2 = geometry.quad_2d(size=(0.5, 0.5), pos=(0.25, 0.75))

        # Programs
        self.linearize_depth_program = self.load_program('programs/linearize_depth.glsl')
        self.linearize_depth_program['near'].value = self.camera.projection.near
        self.linearize_depth_program['far'].value = self.camera.projection.far
        self.basic_light = self.load_program('programs/shadow_mapping/directional_light.glsl')
        self.basic_light['color'].value = 1.0, 1.0, 1.0, 1.0
        self.shadowmap_program = self.load_program('programs/shadow_mapping/shadowmap.glsl')
        self.texture_prog = self.load_program('programs/texture.glsl')
        self.texture_prog['texture0'].value = 0

    def render(self, time, frametime):
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        # --- PASS 1:  Render shadow map
        self.offscreen.clear()
        self.offscreen.use()
        self.shadowmap_program['projection'].write(Matrix44.orthogonal_projection(-10, 10, -10, 10, -10, 20, dtype='f4'))
        self.shadowmap_program['model'].write(Matrix44.identity(dtype='f4'))
        self.shadowmap_program['view'].write(Matrix44.look_at((-10, math.sin(time/10) * 10, 0), (0, 0, 0), (0, 1, 0), dtype='f4'))

        self.floor.render(self.shadowmap_program)
        self.wall.render(self.shadowmap_program)

        # --- PASS 2:  Render scene to screen
        self.wnd.use()
        self.basic_light['m_proj'].write(self.camera.projection.matrix)
        self.basic_light['m_camera'].write(self.camera.matrix)
        self.basic_light['m_model'].write(Matrix44.from_translation((0, -5, -12), dtype='f4'))

        self.floor.render(self.basic_light)
        self.wall.render(self.basic_light)

        # --- PASS 3: Debug ---
        self.ctx.enable_only(moderngl.NOTHING)
        self.offscreen_depth.use()
        self.offscreen_depth.compare_func = ''
        self.offscreen_quad.render(self.linearize_depth_program)
        self.offscreen_color.use(location=0)
        self.offscreen_quad2.render(self.texture_prog)


if __name__ == '__main__':
    moderngl_window.run_window_config(ShadowMapping)