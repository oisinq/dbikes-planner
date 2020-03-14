package io.oisin.fyp;

import android.content.Context;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;

import com.google.android.material.bottomsheet.BottomSheetBehavior;

import androidx.coordinatorlayout.widget.CoordinatorLayout;

/**
 * Created by Oisin Quinn (@oisin1001) on 2020-03-14.
 */
public class CustomBottomSheetBehavior<V extends View> extends BottomSheetBehavior<V> {


    private boolean enableCollapse = false;

    public CustomBottomSheetBehavior() {
    }

    public CustomBottomSheetBehavior(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    public void setEnableCollapse(boolean enableCollapse) {
        this.enableCollapse = enableCollapse;
    }

    @Override
    public boolean onInterceptTouchEvent(CoordinatorLayout parent, V child, MotionEvent event) {
        if (enableCollapse) {
            return false;
        }

        return super.onInterceptTouchEvent(parent, child, event);

    }
}