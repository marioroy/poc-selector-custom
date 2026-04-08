"""POC Selector 2.1.5 plugin — target_sticky + eager_commit toggles."""

from PyQt5.QtWidgets import QCheckBox, QHBoxLayout
import os

SYSCTL_TARGET_STICKY = "/proc/sys/kernel/sched_poc_target_sticky"
SYSCTL_EAGER_COMMIT  = "/proc/sys/kernel/sched_poc_eager_commit"


def _sysctl_read(path):
    try:
        with open(path) as f:
            return int(f.read().strip())
    except Exception:
        return -1


def _sysctl_write(path, val):
    try:
        with open(path, "w") as f:
            f.write(str(val))
        return True
    except Exception:
        return False


def _make_toggle(layout, label, tooltip, sysctl_path):
    """Create a checkbox bound to a boolean sysctl."""
    writable = os.access(sysctl_path, os.W_OK)
    chk = QCheckBox(label)
    chk.setToolTip(tooltip)
    cur = _sysctl_read(sysctl_path)
    if cur >= 0:
        chk.setChecked(bool(cur))
    if not writable:
        chk.setEnabled(False)
        chk.setToolTip("root required")
    chk.stateChanged.connect(
        lambda s: _sysctl_write(sysctl_path, 1 if s else 0))
    layout.addWidget(chk)
    return chk


def setup(layout):
    """Called by MainWindow to populate plugin controls row."""
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)

    _make_toggle(row, "Target sticky",
        "sched_poc_target_sticky: if target CPU is idle, return it "
        "immediately for L1/TLB cache affinity (default: OFF)",
        SYSCTL_TARGET_STICKY)
    row.addSpacing(15)

    _make_toggle(row, "Eager commit",
        "sched_poc_eager_commit: commit selection to idle bitmap "
        "(atomic64_andnot) at selection time to close the race window "
        "where multiple wakers select the same idle CPU (default: ON)",
        SYSCTL_EAGER_COMMIT)
    row.addSpacing(15)

    row.addStretch()
    layout.addLayout(row)

