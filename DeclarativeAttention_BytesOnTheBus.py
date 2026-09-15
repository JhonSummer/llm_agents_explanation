"""Declarative Attention — bytes on the bus.

Merge of GPU-basics chrome (captions, persistent GPU, color contract)
with the DA storyboard (packets, duration=cost, dim-in-place, tags).

Thesis on screen: Read less KV. Move no KV.
Paper: arXiv:2609.02737. Per-token bar matches lit blocks.
The −52% figure is the Gemma-4-31B full-response average, captioned separately.
"""

from manim import *
import numpy as np

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30
config.background_color = BLACK

CHUNK_COLORS = [TEAL, GOLD, "#e07a5f", MAROON_A]
CHUNK_NAMES = ["C1", "C2", "C3", "C4"]
SYS_COLOR = GREY_A
RESP_COLOR = GREEN_B
WEIGHT_COLOR = ORANGE
SM_COLOR = PURPLE
L2_COLOR = BLUE
VRAM_COLOR = RED
rng = np.random.default_rng(7)


def cap_text(text, color=WHITE, fs=28):
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    grp = VGroup(*[Text(ln, font_size=fs, color=color) for ln in lines])
    grp.arrange(DOWN, buff=0.08)
    grp.to_edge(DOWN, buff=0.22)
    grp.set_z_index(60)
    return grp


class DeclarativeAttentionBytes(Scene):
    def construct(self):
        self._cap = VGroup()
        self._chapter = VGroup()
        self._build_chrome()
        self._build_stage()

        self._beat_empty()
        self._beat_weights()
        self._beat_request()
        self._beat_prefill()
        self._beat_vanilla()
        self._beat_focus()
        self._beat_global_local()
        self._beat_punchline()

        keep = {self.band}
        self.play(*[FadeOut(m) for m in list(self.mobjects) if m not in keep], run_time=0.8)

    # ---------------------------------------------------------------- chrome
    def _build_chrome(self):
        self.band = Rectangle(
            width=config.frame_width + 0.4,
            height=1.18,
            fill_color=BLACK,
            fill_opacity=0.92,
            stroke_width=0,
        ).to_edge(DOWN, buff=0)
        self.band.set_z_index(50)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=GREY_E, stroke_width=1)
        rule.next_to(self.band, UP, buff=0).set_z_index(51)
        mark = Text("DECLARATIVE ATTENTION", font_size=16, color=GREY_B)
        mark.to_corner(UL, buff=0.28).set_z_index(52)
        thesis = Text("Read less KV.  Move no KV.", font_size=16, color=GREY_A)
        thesis.next_to(mark, DOWN, buff=0.08).align_to(mark, LEFT).set_z_index(52)
        self.add(self.band, rule, mark, thesis)
        self.thesis = thesis

    def caption(self, text, color=WHITE, hold=0.0):
        new = cap_text(text, color=color)
        if len(self._cap):
            self.remove(self._cap)
        self.play(FadeIn(new), run_time=0.2)
        self._cap = new
        if hold:
            self.wait(hold)
        return new

    def chapter(self, text):
        new = Text(text, font_size=18, color=GREY_A).to_corner(UR, buff=0.28)
        new.set_z_index(52)
        if len(self._chapter):
            self.remove(self._chapter)
        self.add(new)
        self._chapter = new

    def set_mode(self, name, color):
        pill = Text(name, font_size=18, color=color)
        pill.next_to(self.bar_track, DOWN, buff=0.12).align_to(self.bar_track, LEFT)
        if getattr(self, "mode_pill", None) is not None:
            self.play(FadeOut(self.mode_pill), FadeIn(pill), run_time=0.25)
            self.remove(self.mode_pill)
        else:
            self.play(FadeIn(pill), run_time=0.25)
        self.mode_pill = pill

    # ---------------------------------------------------------------- stage
    def _build_stage(self):
        self.gpu = RoundedRectangle(
            corner_radius=0.08,
            width=7.60,
            height=6.00,
            color=GREEN,
            stroke_width=3,
        ).move_to([-2.70, 0.48, 0])
        self.gpu_t = Text("GPU", font_size=20, color=GREEN)
        self.gpu_t.next_to(self.gpu.get_corner(UR), DOWN, buff=0.10).align_to(self.gpu, RIGHT).shift(0.18 * LEFT)

        sms = VGroup()
        for _ in range(12):
            cell = RoundedRectangle(
                corner_radius=0.04,
                width=1.10,
                height=0.50,
                color=SM_COLOR,
                fill_color=SM_COLOR,
                fill_opacity=0.5,
                stroke_width=1.5,
            )
            lab = Text("SM", font_size=16, color=WHITE).move_to(cell)
            sms.add(VGroup(cell, lab))
        sms.arrange_in_grid(3, 4, buff=0.10)
        sms.move_to([self.gpu.get_center()[0], 2.55, 0])
        self.sms = sms
        self.sms_body = VGroup(*[g[0] for g in sms])

        self.l2 = RoundedRectangle(
            corner_radius=0.05,
            width=7.05,
            height=0.56,
            color=L2_COLOR,
            fill_color=L2_COLOR,
            fill_opacity=0.55,
            stroke_width=2,
        ).move_to([self.gpu.get_center()[0], 1.28, 0])
        self.l2_t = Text("L2  ·  the bus", font_size=20, color=WHITE).move_to(self.l2)

        self.vram = RoundedRectangle(
            corner_radius=0.06,
            width=7.05,
            height=2.42,
            color=VRAM_COLOR,
            fill_color=VRAM_COLOR,
            fill_opacity=0.08,
            stroke_width=2.5,
        ).move_to([self.gpu.get_center()[0], -0.88, 0])
        self.vram_t = Text("VRAM (HBM)", font_size=18, color=VRAM_COLOR)
        self.vram_t.next_to(self.vram, DOWN, buff=0.08).align_to(self.vram, LEFT)

        self.weights = RoundedRectangle(
            corner_radius=0.04,
            width=6.55,
            height=0.36,
            color=WEIGHT_COLOR,
            fill_color=WEIGHT_COLOR,
            fill_opacity=0.0,
            stroke_width=1.5,
            stroke_color=WEIGHT_COLOR,
        ).move_to([self.vram.get_center()[0], self.vram.get_top()[1] - 0.32, 0])
        self.weights_t = Text("weights", font_size=18, color=WEIGHT_COLOR)
        self.weights_t.move_to(self.weights).set_opacity(0)

        seats = VGroup()
        for _ in range(5):
            seats.add(
                RoundedRectangle(
                    corner_radius=0.05,
                    width=1.18,
                    height=1.00,
                    color=GREY_E,
                    fill_opacity=0.0,
                    stroke_width=1.5,
                )
            )
        seats.arrange(RIGHT, buff=0.12)
        seats.move_to([self.vram.get_center()[0], -0.85, 0])
        self.seats = seats

        self.host = RoundedRectangle(
            corner_radius=0.08,
            width=4.20,
            height=6.00,
            color=GREY_C,
            stroke_width=3,
        ).move_to([4.55, 0.48, 0])
        self.host_title = Text("host (CPU + RAM)", font_size=20, color=GREY_B)
        self.host_title.next_to(self.host.get_top(), DOWN, buff=0.16)

        pcie_left = self.gpu.get_right()[0]
        pcie_right = self.host.get_left()[0]
        self.pcie_y = self.weights.get_center()[1]
        self.pcie = RoundedRectangle(
            corner_radius=0.04,
            width=pcie_right - pcie_left - 0.08,
            height=0.52,
            color=GREY_B,
            fill_color=GREY_E,
            fill_opacity=0.25,
            stroke_width=2,
        ).move_to([(pcie_left + pcie_right) / 2, self.pcie_y, 0])
        self.pcie_t = Text("PCIe", font_size=18, color=GREY_B).next_to(self.pcie, UP, buff=0.08)

        self.bar_track = Rectangle(width=3.50, height=0.40, color=GREY_B, stroke_width=2)
        self.bar_track.move_to([self.host.get_center()[0] - 0.12, -1.62, 0])
        self.bar_label = Text("KV bytes / token", font_size=18, color=GREY_B)
        self.bar_label.next_to(self.bar_track, UP, buff=0.10).align_to(self.bar_track, LEFT)
        self.bar = self._bar_fill(0.001, GREY_B)
        self.pct = Text("", font_size=24, color=GREY_B).next_to(self.bar_track, RIGHT, buff=0.10)
        self.mode_pill = None
        self.host_body = VGroup()
        self.out_lines = []
        self.resp_tiles = VGroup()
        self.kv_blocks = []
        self.kv_labels = []

    def _bar_fill(self, frac, color):
        w = max(self.bar_track.width * frac, 0.04)
        f = Rectangle(width=w, height=self.bar_track.height - 0.04, stroke_width=0,
                      fill_color=color, fill_opacity=0.9)
        f.align_to(self.bar_track, LEFT).align_to(self.bar_track, DOWN).shift(0.02 * UP + 0.02 * RIGHT)
        return f

    # ---------------------------------------------------------------- packets
    def _packet(self, start, end, color, via=None, side=0.24, move=0.70):
        sq = Square(side_length=side, fill_color=color, fill_opacity=1.0,
                    stroke_width=1.0, stroke_color=WHITE, stroke_opacity=0.4)
        sq.set_z_index(20)
        sq.move_to(start)
        if via is None:
            path = Line(start, end)
        else:
            path = VMobject().set_points_as_corners(
                [np.array(start), np.array(via), np.array(end)]
            )
        anim = Succession(
            FadeIn(sq, run_time=0.06),
            MoveAlongPath(sq, path, run_time=move),
            FadeOut(sq, run_time=0.08),
        )
        return sq, anim

    def stream_pcie(self, src, dst, color, n=10, via_sms=False):
        items = []
        for _ in range(n):
            sy = src.get_center()[1] + rng.uniform(-0.28, 0.28) * src.height
            start = np.array([src.get_left()[0], sy, 0])
            wy = self.pcie.get_center()[1] + rng.uniform(-0.12, 0.12)
            mid1 = np.array([self.pcie.get_right()[0] - 0.04, wy, 0])
            mid0 = np.array([self.pcie.get_left()[0] + 0.04, wy, 0])
            if via_sms:
                ex = self.sms.get_center()[0] + rng.uniform(-0.4, 0.4) * self.sms.width
                end = np.array([ex, self.sms.get_bottom()[1] + 0.02, 0])
                via = [mid1, mid0, np.array([end[0], self.l2.get_center()[1], 0])]
                path_pts = [start] + via + [end]
                path = VMobject().set_points_as_corners(path_pts)
                sq = Square(side_length=0.24, fill_color=color, fill_opacity=1.0,
                            stroke_width=1.0, stroke_color=WHITE, stroke_opacity=0.4).set_z_index(20)
                sq.move_to(start)
                anim = Succession(
                    FadeIn(sq, run_time=0.06),
                    MoveAlongPath(sq, path, run_time=0.70),
                    FadeOut(sq, run_time=0.08),
                )
                items.append((sq, anim))
            else:
                ex = dst.get_center()[0] + rng.uniform(-0.35, 0.35) * dst.width
                end = np.array([ex, dst.get_center()[1], 0])
                via = np.array([end[0], wy, 0])
                items.append(self._packet(start, end, color, via=via, move=0.70))
        rng.shuffle(items)
        packets = [p for p, _ in items]
        return packets, LaggedStart(*[a for _, a in items], lag_ratio=0.05)

    def stream_up(self, srcs, n_per=3, move=0.70):
        items = []
        l2y = self.l2.get_center()[1]
        for s in srcs:
            col = s.get_fill_color()
            for _ in range(n_per):
                sx = s.get_center()[0] + rng.uniform(-0.32, 0.32) * s.width
                start = np.array([sx, s.get_top()[1], 0])
                mx = self.l2.get_center()[0] + rng.uniform(-0.4, 0.4) * self.l2.width
                via = np.array([mx, l2y, 0])
                ex = self.sms.get_center()[0] + rng.uniform(-0.42, 0.42) * self.sms.width
                end = np.array([ex, self.sms.get_bottom()[1] - 0.02, 0])
                items.append(self._packet(start, end, col, via=via, move=move))
        rng.shuffle(items)
        packets = [p for p, _ in items]
        return packets, LaggedStart(*[a for _, a in items], lag_ratio=0.04)

    def stream_write(self, block, n=5):
        items = []
        col = block.get_fill_color()
        l2y = self.l2.get_center()[1]
        for _ in range(n):
            sx = self.sms.get_center()[0] + rng.uniform(-0.4, 0.4) * self.sms.width
            start = np.array([sx, self.sms.get_bottom()[1], 0])
            via = np.array([block.get_center()[0], l2y, 0])
            ex = block.get_center()[0] + rng.uniform(-0.28, 0.28) * block.width
            end = np.array([ex, block.get_top()[1], 0])
            items.append(self._packet(start, end, col, via=via, move=0.55))
        packets = [p for p, _ in items]
        return packets, LaggedStart(*[a for _, a in items], lag_ratio=0.06)

    def play_stream(self, packets, stream, *extra, run_time=1.2):
        self.play(stream, *extra, run_time=run_time)
        self.remove(*packets)

    # ---------------------------------------------------------------- beats
    def _beat_empty(self):
        self.chapter("1  Empty GPU")
        self.play(Create(self.gpu), FadeIn(self.gpu_t), run_time=0.8)
        self.play(
            LaggedStart(*[FadeIn(g) for g in self.sms], lag_ratio=0.04),
            FadeIn(self.l2), FadeIn(self.l2_t),
            run_time=1.0,
        )
        self.play(Create(self.vram), FadeIn(self.vram_t), FadeIn(self.seats), run_time=0.7)
        self.caption("Empty GPU. Compute on top. Memory below.", hold=2.2)

        self.play(Create(self.host), FadeIn(self.host_title), run_time=0.6)
        self.play(FadeIn(self.pcie), FadeIn(self.pcie_t), run_time=0.4)
        self.caption("GPU computes. Host coordinates. PCIe connects them.", hold=1.6)

    def _beat_weights(self):
        self.chapter("2  Load weights")
        ckpt = Text("model checkpoint", font_size=18, color=GREY_B)
        box = RoundedRectangle(
            corner_radius=0.05, width=3.2, height=1.15,
            color=WEIGHT_COLOR, fill_color=WEIGHT_COLOR, fill_opacity=0.55, stroke_width=2,
        )
        box_t = Text("weights", font_size=20, color=WHITE).move_to(box)
        body = VGroup(ckpt, VGroup(box, box_t)).arrange(DOWN, buff=0.18)
        body.next_to(self.host_title, DOWN, buff=0.35)
        self.host_body = body
        self.play(FadeIn(body), FadeIn(self.weights), run_time=0.6)
        self.caption("Weights cross PCIe and stay in VRAM.")
        packets, stream = self.stream_pcie(box, self.weights, WEIGHT_COLOR, n=12)
        self.play_stream(
            packets, stream,
            self.weights.animate.set_fill(WEIGHT_COLOR, 0.85),
            self.weights_t.animate.set_opacity(1.0),
            box.animate.set_opacity(0.35),
            run_time=1.8,
        )
        self.caption("Same GPU. Weights resident. VRAM is no longer empty.", hold=1.8)

    def _beat_request(self):
        self.chapter("3  Prefill")
        self.play(FadeOut(self.host_body), run_time=0.35)
        title = Text("the request", font_size=20, color=GREY_B)
        rows = VGroup()
        sys_r = RoundedRectangle(
            corner_radius=0.04, width=3.35, height=0.46,
            color=SYS_COLOR, fill_color=SYS_COLOR, fill_opacity=0.6, stroke_width=1.5,
        )
        sys_l = Text("SYS + question", font_size=18, color=WHITE).move_to(sys_r)
        rows.add(VGroup(sys_r, sys_l))
        self.req_rects = [sys_r]
        for name, col in zip(CHUNK_NAMES, CHUNK_COLORS):
            r = RoundedRectangle(
                corner_radius=0.04, width=3.35, height=0.46,
                color=col, fill_color=col, fill_opacity=0.6, stroke_width=1.5,
            )
            lab = Text(f"magic chunk  {name}", font_size=18, color=WHITE).move_to(r)
            rows.add(VGroup(r, lab))
            self.req_rects.append(r)
        rows.arrange(DOWN, buff=0.12)
        body = VGroup(title, rows).arrange(DOWN, buff=0.18)
        body.next_to(self.host_title, DOWN, buff=0.28)
        self.host_body = body
        self.req_rows = rows
        self.play(
            Transform(self.host_title, Text("host  ·  request", font_size=20, color=GREY_B).move_to(self.host_title)),
            FadeIn(body),
            run_time=0.7,
        )
        self.caption("A long request, split into ~2K-token magic chunks.", hold=1.6)

    def _beat_prefill(self):
        self.caption("Prefill: SMs turn each chunk into keys and values.")
        specs = [("SYS", SYS_COLOR)] + list(zip(CHUNK_NAMES, CHUNK_COLORS))
        self.kv_blocks = []
        self.kv_labels = []
        for i, ((name, col), seat, src) in enumerate(zip(specs, self.seats, self.req_rects)):
            p1, s1 = self.stream_pcie(src, None, col, n=8, via_sms=True)
            self.play_stream(p1, s1, src.animate.set_opacity(0.35), run_time=0.7)
            block = RoundedRectangle(
                corner_radius=0.05, width=1.18, height=1.00,
                color=col, fill_color=col, fill_opacity=0.0, stroke_width=1.5,
            ).move_to(seat)
            lab = Text(name, font_size=18, color=WHITE).move_to(block)
            lab.set_opacity(0)
            self.add(block, lab)
            p2, s2 = self.stream_write(block, n=5)
            extras = [block.animate.set_fill(col, 0.7), lab.animate.set_opacity(1.0)]
            if i == 0:
                kv_t = Text("KV cache", font_size=18, color=RED_A)
                kv_t.next_to(self.seats, DOWN, buff=0.10).align_to(self.seats, LEFT)
                extras.append(FadeIn(kv_t))
                self.kv_t = kv_t
            self.play_stream(p2, s2, *extras, run_time=0.55)
            self.kv_blocks.append(block)
            self.kv_labels.append(lab)
        self.sys_block = self.kv_blocks[0]
        self.chunk_blocks = self.kv_blocks[1:]
        self.chunk_labels = self.kv_labels[1:]
        self.caption("Prefill done. KV sits in VRAM and does not move again.", hold=2.0)

    def _replace_host_output(self):
        self.play(FadeOut(self.host_body), run_time=0.35)
        self.host_body = VGroup()
        new_title = Text("host  ·  output", font_size=20, color=GREY_B).move_to(self.host_title)
        self.play(Transform(self.host_title, new_title), run_time=0.3)
        self.out_title = Text("model output", font_size=18, color=GREY_B)
        self.out_title.next_to(self.host_title, DOWN, buff=0.28).align_to(self.host.get_left(), LEFT).shift(0.28 * RIGHT)
        self.play(
            FadeIn(self.out_title),
            Create(self.bar_track), FadeIn(self.bar_label),
            run_time=0.6,
        )
        self.add(self.bar, self.pct)
        resp_lab = Text("resp", font_size=18, color=RESP_COLOR)
        resp_lab.next_to(self.vram.get_bottom(), UP, buff=0.18).align_to(self.vram, LEFT).shift(0.12 * RIGHT)
        self.resp_lab = resp_lab
        self.play(FadeIn(resp_lab), run_time=0.25)
        self.out_cursor = self.out_title.get_bottom() + 0.28 * DOWN

    def _out_word(self, text, color=GREY_B, fs=18, newline=False):
        t = Text(text, font_size=fs, color=color)
        if t.width > 3.6:
            t.scale_to_fit_width(3.6)
        if newline or not self.out_lines:
            if self.out_lines:
                t.next_to(self.out_lines[-1], DOWN, buff=0.14, aligned_edge=LEFT)
            else:
                t.next_to(self.out_title, DOWN, buff=0.22)
                t.align_to(self.out_title, LEFT)
            self.out_lines.append(t)
        else:
            t.next_to(self.out_lines[-1], RIGHT, buff=0.12)
            t.align_to(self.out_lines[-1], DOWN)
            if t.get_right()[0] > self.host.get_right()[0] - 0.25:
                t.next_to(self.out_lines[-1], DOWN, buff=0.14, aligned_edge=LEFT)
                t.align_to(self.out_title, LEFT)
            self.out_lines.append(t)
        return t

    def _add_resp_tile(self):
        tile = RoundedRectangle(
            corner_radius=0.03, width=0.34, height=0.30,
            color=RESP_COLOR, fill_color=RESP_COLOR, fill_opacity=0.7, stroke_width=1,
        )
        if len(self.resp_tiles) == 0:
            tile.next_to(self.resp_lab, RIGHT, buff=0.12)
            tile.align_to(self.resp_lab, DOWN)
        else:
            tile.next_to(self.resp_tiles[-1], RIGHT, buff=0.07)
        self.resp_tiles.add(tile)
        return tile

    def decode_step(self, srcs, word=None, word_color=GREY_B, rt=2.4,
                    frac=1.0, bcol=RED, pct="100%", pcol=RED, n_per=3, newline=False):
        tile = self._add_resp_tile()
        live = list(srcs) + list(self.resp_tiles[:-1])
        packets, stream = self.stream_up(live, n_per=n_per, move=max(0.45, rt * 0.45))
        extra = [
            FadeIn(tile),
            Transform(self.bar, self._bar_fill(frac, bcol)),
            self.l2.animate.set_stroke(YELLOW if frac > 0.7 else WHITE, 4 if frac > 0.7 else 2).set_fill(L2_COLOR, 0.85 if frac > 0.7 else 0.55),
        ]
        if word is not None:
            extra.append(FadeIn(self._out_word(word, color=word_color, newline=newline)))
        if pct is not None:
            newp = Text(pct, font_size=24, color=pcol).next_to(self.bar_track, RIGHT, buff=0.10)
            extra.append(Transform(self.pct, newp))
        self.play_stream(packets, stream, *extra, run_time=rt)

    def _beat_vanilla(self):
        self.chapter("4  Vanilla decode")
        self._replace_host_output()
        self.set_mode("VANILLA", RED)
        self.caption("Generating: each new token must reread the old keys.")
        full = [self.sys_block] + self.chunk_blocks
        self.decode_step(full, word="Scanning", rt=2.40, frac=1.0, bcol=RED, pct="100%", pcol=RED, n_per=3)
        self.decode_step(full, word="the context…", rt=2.40, frac=1.0, bcol=RED, pct="100%", pcol=RED, n_per=3)
        self.caption("Every token rereads the full KV. The bus sets the speed.", hold=2.0)

    def _beat_focus(self):
        self.chapter("5  Focus")
        self.set_mode("FOCUS", YELLOW)
        self.caption("The model writes where it needs to look — in its own output.")
        tag = self._out_word('<focus chunks="3">', color=YELLOW, fs=18, newline=True)
        box = SurroundingRectangle(tag, color=YELLOW, buff=0.07)
        self.play(FadeIn(tag), Create(box), run_time=0.7)
        self.tag_box = box
        masked = [b for i, b in enumerate(self.chunk_blocks) if i != 2]
        masked_l = [l for i, l in enumerate(self.chunk_labels) if i != 2]
        note = Text("still resident", font_size=18, color=GREY_B)
        note.next_to(self.kv_t, RIGHT, buff=0.25)
        self.play(
            *[b.animate.set_fill(opacity=0.16).set_stroke(opacity=0.55) for b in masked],
            *[l.animate.set_opacity(0.50) for l in masked_l],
            FadeIn(note),
            run_time=0.9,
        )
        self.mask_note = note
        self.caption("The engine parses the tag. Unused KV dims. It is still there.", hold=1.4)

        focus = [self.sys_block, self.chunk_blocks[2]]
        self.decode_step(focus, word="Chunk 3", rt=0.90, frac=0.40, bcol=GREEN, pct="40%", pcol=GREEN, n_per=3, newline=True)
        self.decode_step(focus, word="has the date.", rt=0.90, frac=0.40, bcol=GREEN, pct="40%", pcol=GREEN, n_per=3)
        self.caption(
            "This step reads SYS + C3. Across a whole decode:\n"
            "Gemma-4-31B attends 52% fewer tokens, −1.3pp.",
            hold=2.6,
        )

    def _beat_global_local(self):
        self.chapter("6  Global")
        gl = self._out_word("<global>", color=BLUE_B, fs=18, newline=True)
        masked = [b for i, b in enumerate(self.chunk_blocks) if i != 2]
        masked_l = [l for i, l in enumerate(self.chunk_labels) if i != 2]
        self.play(
            FadeIn(gl),
            *[b.animate.set_fill(opacity=0.70).set_stroke(opacity=1.0) for b in masked],
            *[l.animate.set_opacity(1.0) for l in masked_l],
            FadeOut(self.mask_note),
            FadeOut(self.tag_box),
            run_time=0.8,
        )
        self.set_mode("GLOBAL", BLUE_B)
        self.caption("<global> surveys the full context when it needs to look around.")
        full = [self.sys_block] + self.chunk_blocks
        self.decode_step(full, word="Cross-checking…", rt=2.00, frac=1.0, bcol=RED, pct="100%", pcol=RED, n_per=3, newline=True)

        self.chapter("7  Local")
        lo = self._out_word("<local>", color=RESP_COLOR, fs=18, newline=True)
        self.play(
            FadeIn(lo),
            *[b.animate.set_fill(opacity=0.16).set_stroke(opacity=0.55) for b in self.chunk_blocks],
            *[l.animate.set_opacity(0.50) for l in self.chunk_labels],
            run_time=0.7,
        )
        self.set_mode("LOCAL", RESP_COLOR)
        self.caption("<local> drops every magic chunk. Scaffold + the reply stay.", hold=0.8)
        only = [self.sys_block]
        self.decode_step(only, word="<answer>8 years</answer>", word_color=WHITE, rt=0.70,
                         frac=0.08, bcol=GREEN, pct="~8%", pcol=GREEN, n_per=2, newline=True)

    def _beat_punchline(self):
        self.chapter("8  The point")
        self.play(
            *[b.animate.set_fill(opacity=0.70).set_stroke(opacity=1.0) for b in self.chunk_blocks],
            *[l.animate.set_opacity(1.0) for l in self.chunk_labels],
            run_time=0.6,
        )
        self.caption(
            "No KV block ever moved.\nDA only changed which bytes cross the bus.",
            color=YELLOW,
        )
        self.play(
            LaggedStart(*[Indicate(b, color=YELLOW, scale_factor=1.06) for b in self.kv_blocks], lag_ratio=0.08),
            run_time=1.6,
        )
        end = Text("KV never moved.", font_size=32, color=YELLOW)
        end.to_edge(UP, buff=0.12)
        self.play(FadeIn(end, shift=0.1 * UP), run_time=0.5)
        self.wait(2.8)
