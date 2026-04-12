import UIKit
import Capacitor
import WebKit

@objc(LoadingViewController)
class LoadingViewController: CAPBridgeViewController {

    private var loadingOverlay: UIView?
    private var fillConstraint: NSLayoutConstraint?
    private var overlayShown = false
    private var kvoToken: NSKeyValueObservation?
    private var fallbackTimer: Timer?
    private var dismissing = false

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        // Paint the navy background immediately so the WKWebView's black default
        // never shows through before the overlay or HTML is ready.
        view.backgroundColor = UIColor(red: 10/255, green: 22/255, blue: 40/255, alpha: 1)
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard !overlayShown else { return }
        overlayShown = true
        addLoadingOverlay()

        // Start a guaranteed fallback timer immediately — this fires regardless of
        // whether KVO attaches successfully, so the overlay always eventually dismisses.
        fallbackTimer = Timer.scheduledTimer(withTimeInterval: 10, repeats: false) { [weak self] _ in
            self?.completeAndDismiss()
        }

        attachKVO()
    }

    deinit {
        kvoToken?.invalidate()
        fallbackTimer?.invalidate()
    }

    // MARK: - KVO

    private func attachKVO(attempt: Int = 0) {
        // Prefer Capacitor's own bridge.webView property; fall back to subview traversal.
        let wv = bridge?.webView ?? findWebView(in: view)

        guard let wv else {
            // WebView not ready yet — retry up to ~3 seconds (30 × 100ms)
            guard attempt < 30 else { return }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { [weak self] in
                self?.attachKVO(attempt: attempt + 1)
            }
            return
        }

        // Ensure the WebView itself is never black while content loads
        wv.isOpaque = false
        wv.backgroundColor = UIColor(red: 10/255, green: 22/255, blue: 40/255, alpha: 1)
        wv.scrollView.backgroundColor = UIColor(red: 10/255, green: 22/255, blue: 40/255, alpha: 1)

        kvoToken = wv.observe(\.estimatedProgress, options: [.new]) { [weak self] webView, _ in
            DispatchQueue.main.async {
                let p = webView.estimatedProgress
                let mapped = min(p * 0.90, 0.90)
                self?.setProgress(mapped, animated: true)
                if p >= 0.99 {
                    self?.kvoToken?.invalidate()
                    self?.kvoToken = nil
                    self?.completeAndDismiss()
                }
            }
        }
    }

    // MARK: - Overlay

    private func addLoadingOverlay() {
        let overlay = UIView(frame: view.bounds)
        overlay.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        overlay.backgroundColor = UIColor(red: 10/255, green: 22/255, blue: 40/255, alpha: 1)

        // Splash image — check Assets.xcassets for the exact asset name
        let splash = UIImageView(image: UIImage(named: "Splash"))
        splash.contentMode = .scaleAspectFill
        splash.frame = overlay.bounds
        splash.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        overlay.addSubview(splash)

        // Custom progress bar: track + fill
        let trackH: CGFloat = 8
        let track = UIView()
        track.backgroundColor = UIColor(red: 30/255, green: 58/255, blue: 95/255, alpha: 0.8)
        track.layer.cornerRadius = trackH / 2
        track.clipsToBounds = true
        track.translatesAutoresizingMaskIntoConstraints = false
        overlay.addSubview(track)

        let fill = UIView()
        fill.backgroundColor = UIColor(red: 212/255, green: 134/255, blue: 60/255, alpha: 1)
        fill.layer.cornerRadius = trackH / 2
        fill.clipsToBounds = true
        fill.translatesAutoresizingMaskIntoConstraints = false
        track.addSubview(fill)

        let fillW = fill.widthAnchor.constraint(equalToConstant: 0)
        fillW.isActive = true
        fillConstraint = fillW

        NSLayoutConstraint.activate([
            track.centerXAnchor.constraint(equalTo: overlay.centerXAnchor),
            track.centerYAnchor.constraint(equalTo: overlay.centerYAnchor),
            track.widthAnchor.constraint(equalTo: overlay.widthAnchor, multiplier: 0.55),
            track.heightAnchor.constraint(equalToConstant: trackH),
            fill.leadingAnchor.constraint(equalTo: track.leadingAnchor),
            fill.topAnchor.constraint(equalTo: track.topAnchor),
            fill.bottomAnchor.constraint(equalTo: track.bottomAnchor),
        ])

        view.addSubview(overlay)
        view.bringSubviewToFront(overlay)
        loadingOverlay = overlay

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) { [weak self] in
            self?.setProgress(0.05, animated: true)
        }
    }

    private func setProgress(_ fraction: CGFloat, animated: Bool) {
        guard let overlay = loadingOverlay, let fillW = fillConstraint else { return }
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
