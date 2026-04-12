import UIKit
import Capacitor
import WebKit

class LoadingViewController: CAPBridgeViewController {

    private var loadingOverlay: UIView?
    private var fillConstraint: NSLayoutConstraint?
    private var overlayShown = false
    private var kvoToken: NSKeyValueObservation?
    private var fallbackTimer: Timer?
    private var dismissing = false

    // MARK: - Lifecycle

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard !overlayShown else { return }
        overlayShown = true
        addLoadingOverlay()
        startProgressObservation()
    }

    deinit {
        kvoToken?.invalidate()
        fallbackTimer?.invalidate()
    }

    // MARK: - Overlay

    private func addLoadingOverlay() {
        let overlay = UIView(frame: view.bounds)
        overlay.autoresizingMask = [.flexibleWidth, .flexibleHeight]

        // Splash background — same image used on the launch screen
        let splash = UIImageView(image: UIImage(named: "Splash"))
        splash.contentMode = .scaleAspectFill
        splash.frame = overlay.bounds
        splash.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        overlay.addSubview(splash)

        // Custom progress bar: track + fill (avoids UIProgressView transform quirks)
        let trackH: CGFloat = 8

        let track = UIView()
        track.backgroundColor = UIColor(red: 30/255, green: 58/255, blue: 95/255, alpha: 0.8)
        track.layer.cornerRadius = trackH / 2
        track.clipsToBounds = true
        track.translatesAutoresizingMaskIntoConstraints = false
        overlay.addSubview(track)

        let fill = UIView()
        fill.backgroundColor = UIColor(red: 212/255, green: 134/255, blue: 60/255, alpha: 1) // #d4863c
        fill.layer.cornerRadius = trackH / 2
        fill.clipsToBounds = true
        fill.translatesAutoresizingMaskIntoConstraints = false
        track.addSubview(fill)

        // Fill starts at 0 width; we'll animate it via the constraint
        let fillW = fill.widthAnchor.constraint(equalToConstant: 0)
        fillW.isActive = true
        fillConstraint = fillW

        NSLayoutConstraint.activate([
            // Track: centered, 55% wide, fixed height
            track.centerXAnchor.constraint(equalTo: overlay.centerXAnchor),
            track.centerYAnchor.constraint(equalTo: overlay.centerYAnchor),
            track.widthAnchor.constraint(equalTo: overlay.widthAnchor, multiplier: 0.55),
            track.heightAnchor.constraint(equalToConstant: trackH),

            // Fill: pinned to left edge of track, full height
            fill.leadingAnchor.constraint(equalTo: track.leadingAnchor),
            fill.topAnchor.constraint(equalTo: track.topAnchor),
            fill.bottomAnchor.constraint(equalTo: track.bottomAnchor),
        ])

        view.addSubview(overlay)
        view.bringSubviewToFront(overlay)
        loadingOverlay = overlay

        // Animate fill to ~5% immediately so something is visibly moving
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) { [weak self] in
            self?.setProgress(0.05, animated: true)
        }
    }

    private func setProgress(_ fraction: CGFloat, animated: Bool) {
        guard let overlay = loadingOverlay, let fillW = fillConstraint else { return }
        // Track width is a fraction of overlay width, so compute absolute track width
        let trackWidth = overlay.bounds.width * 0.55
        let targetWidth = trackWidth * min(fraction, 1.0)
        if animated {
            UIView.animate(withDuration: 0.25) {
                fillW.constant = targetWidth
                overlay.layoutIfNeeded()
            }
        } else {
            fillW.constant = targetWidth
        }
    }

    // MARK: - KVO progress observation

    private func startProgressObservation() {
        guard let wv = findWebView(in: view) else {
            // WebView not added yet — try again shortly
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { [weak self] in
                self?.startProgressObservation()
            }
            return
        }

        kvoToken = wv.observe(\.estimatedProgress, options: [.new]) { [weak self] webView, _ in
            DispatchQueue.main.async {
                let p = webView.estimatedProgress
                // Map WKWebView progress (0–1) to bar progress, reserving last 10% for completion
                let mapped = min(p * 0.90, 0.90)
                self?.setProgress(mapped, animated: true)

                // WKWebView sets estimatedProgress to 1.0 when navigation finishes
                if p >= 0.99 {
                    self?.kvoToken?.invalidate()
                    self?.kvoToken = nil
                    self?.completeAndDismiss()
                }
            }
        }

        // Safety fallback: dismiss after 12 seconds regardless
        fallbackTimer = Timer.scheduledTimer(withTimeInterval: 12, repeats: false) { [weak self] _ in
            self?.completeAndDismiss()
        }
    }

    // MARK: - Dismiss

    private func completeAndDismiss() {
        guard !dismissing else { return }
        dismissing = true
        fallbackTimer?.invalidate()
        kvoToken?.invalidate()
        setProgress(1.0, animated: true)
        UIView.animate(withDuration: 0.35, delay: 0.3) {
            self.loadingOverlay?.alpha = 0
        } completion: { _ in
            self.loadingOverlay?.removeFromSuperview()
            self.loadingOverlay = nil
        }
    }

    // MARK: - Helpers

    private func findWebView(in parent: UIView) -> WKWebView? {
        for sub in parent.subviews {
            if let wv = sub as? WKWebView { return wv }
            if let wv = findWebView(in: sub) { return wv }
        }
        return nil
    }
}
